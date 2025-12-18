#!/usr/bin/env python3
"""
Fetch LGA polygon(s) from an ABS OGC WFS endpoint and save as GeoJSON.

Usage:
    python scripts/fetch_abs_lga.py --lga "Moree" \
        --wfs-url "https://<ABS-WFS-ENDPOINT>/ows" \
        --out-dir data

Notes:
- The ABS documentation page lists the correct WFS endpoints and layer names:
  https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/data-services-and-apis#how-to-use-asgs-geospatial-web-services
- If you omit --layer, the script will try to auto-detect a layer name likely containing 'LGA'.
- The script tries to use a CQL_FILTER (vendor extension common to GeoServer). If the server doesn't support it, the script downloads the layer and filters locally.
"""

import argparse
import logging
import sys
from pathlib import Path
from urllib.parse import urlencode

import geopandas as gpd
import requests
from owslib.wfs import WebFeatureService
import io
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    return s


def try_get_feature_wfs(wfs_url: str, layer: str, cql_param_name: str, lga_name: str):
    """
    Try to request a GeoJSON via WFS GetFeature using a CQL filter parameter name.
    Returns GeoJSON text on success, or raises requests.HTTPError on bad response.
    """
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": layer,
        "outputFormat": "application/json",
        # use count to avoid extremely large downloads (but LGA layer is small)
        "count": 1000,
    }

    # Many servers expect CQL_FILTER or cql_filter; value format depends on server:
    # Try typical attribute names likely to hold LGA name: LGA_NAME, LGA_NAME21, NAME
    # We'll wrap value in single quotes for SQL style matching.
    # Because attribute name can vary across layers, we'll attempt multiple attribute names later.
    # Here we set a generic expression to be adjusted by caller.
    params[cql_param_name] = f"\"LGA_NAME\"='{lga_name}'"

    url = wfs_url.rstrip("?")
    full = url + "?" + urlencode(params)
    logger.debug("Requesting WFS GetFeature: %s", full)
    resp = requests.get(full, timeout=60)
    resp.raise_for_status()
    return resp.text


def download_layer_and_filter_locally(wfs_url: str, layer: str, lga_name: str):
    """
    Download the whole layer as GeoJSON and filter via geopandas by searching text fields for lga_name.
    """
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": layer,
        "outputFormat": "application/json",
    }
    url = wfs_url.rstrip("?") + "?" + urlencode(params)
    logger.info("Downloading full layer (may be large): %s", url)
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    # Load into geopandas from text
    gj_text = resp.text
    gdf = gpd.read_file(io.StringIO(gj_text))
    # Try to find column with names
    text_cols = [c for c in gdf.columns if gdf[c].dtype == object]
    mask = None
    for col in text_cols:
        if gdf[col].str.contains(lga_name, case=False, na=False).any():
            mask = gdf[col].str.contains(lga_name, case=False, na=False)
            logger.info("Filtering by column %s", col)
            break
    if mask is None:
        raise ValueError("Could not locate LGA name in downloaded layer attributes. Inspect layer or provide explicit layer name.")
    return gdf[mask]


def find_lga_feature(wfs_url: str, layer: str, lga_name: str):
    """
    Try multiple strategies to get the LGA feature:
    1) Try common CQL parameter names and attribute names
    2) Fall back to downloading whole layer and filtering locally
    Returns a GeoDataFrame with matched features.
    """
    # candidate CQL param names used by various servers
    cql_param_candidates = ["CQL_FILTER", "cql_filter", "FILTER", "filter"]
    # candidate attribute names used to store LGA names
    attr_name_candidates = ["LGA_NAME", "LGA_NAME21", "LGA_NAME_2021", "NAME", "NAME_2", "NAME_1", "LGA_NAME21"]

    for cql_param in cql_param_candidates:
        # Try each candidate attribute name by substituting into the CQL expression
        for attr in attr_name_candidates:
            try:
                params = {
                    "service": "WFS",
                    "version": "2.0.0",
                    "request": "GetFeature",
                    "typeName": layer,
                    "outputFormat": "application/json",
                    cql_param: f"\"{attr}\"='{lga_name}'",
                }
                url = wfs_url.rstrip("?") + "?" + urlencode(params)
                logger.debug("Trying WFS GetFeature with %s attr %s", cql_param, attr)
                resp = requests.get(url, timeout=60)
                if resp.status_code != 200:
                    logger.debug("Got status %s for %s", resp.status_code, url)
                    continue
                # Load the returned geojson
                try:
                    gdf = gpd.read_file(io.StringIO(resp.text))
                except Exception as e:
                    logger.debug("Failed to read geojson text: %s", e)
                    continue
                if len(gdf) == 0:
                    logger.debug("No features matched for attr %s", attr)
                    continue
                logger.info("Matched %d feature(s) using %s with attr %s", len(gdf), cql_param, attr)
                return gdf
            except requests.HTTPError as he:
                logger.debug("HTTP error with cql attempt: %s", he)
            except Exception as e:
                logger.debug("Exception during cql attempt: %s", e)

    # If we get here, CQL attempts didn't work — fallback to full layer download + local filter
    logger.info("Falling back to downloading layer and filtering locally (safe for LGA layers).")
    return download_layer_and_filter_locally(wfs_url, layer, lga_name)


def auto_detect_lga_layer(wfs_url: str):
    """
    Query WFS capabilities and pick a sensible LGA-like layer if present.
    """
    try:
        wfs = WebFeatureService(url=wfs_url, version="2.0.0")
    except Exception as e:
        raise RuntimeError(f"Failed to connect to WFS at {wfs_url}: {e}")

    candidates = []
    for name, meta in wfs.contents.items():
        lname = name.lower()
        title = (meta.title or "").lower()
        if "lga" in lname or "lga" in title or "local" in lname or "local" in title or "local government" in title:
            candidates.append(name)
    if candidates:
        logger.info("Auto-detected candidate LGA layers: %s", candidates)
        # choose the first candidate
        return candidates[0]
    # If not found, return first layer as a last resort (caller will likely filter locally)
    first = next(iter(wfs.contents.keys()))
    logger.warning("Could not auto-detect LGA layer; defaulting to first layer: %s", first)
    return first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lga", required=True, help="Name (or partial name) of the LGA to fetch (e.g., 'Moree')")
    parser.add_argument("--wfs-url", required=True, help="WFS endpoint URL (see ABS data services page).")
    parser.add_argument("--layer", default=None, help="WFS layer name (optional). If omitted the script tries to auto-detect an LGA layer.")
    parser.add_argument("--out-dir", default="data", help="Directory to write the geojson")
    parser.add_argument("--out-name", default=None, help="Output filename (optional). If omitted uses lga slug.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    lga_name = args.lga.strip()
    wfs_url = args.wfs_url.strip()

    # Determine layer
    layer = args.layer
    if not layer:
        logger.info("Auto-detecting LGA layer from WFS capabilities...")
        layer = auto_detect_lga_layer(wfs_url)
        logger.info("Using layer: %s", layer)

    # Attempt to find LGA feature(s)
    try:
        gdf = find_lga_feature(wfs_url, layer, lga_name)
    except Exception as e:
        logger.error("Failed to retrieve LGA features: %s", e)
        sys.exit(2)

    if gdf is None or gdf.empty:
        logger.error("No features found for LGA '%s' in layer %s", lga_name, layer)
        sys.exit(1)

    # Clean geometry CRS if needed and write to file
    try:
        # Ensure GeoJSON uses EPSG:4326 (GeoJSON canonical)
        if gdf.crs is None:
            logger.warning("Layer has no CRS; assuming EPSG:4326")
            gdf = gdf.set_crs(epsg=4326, allow_override=True)
        else:
            gdf = gdf.to_crs(epsg=4326)
    except Exception:
        pass

    out_name = args.out_name or f"{slugify(lga_name)}.geojson"
    out_path = out_dir / out_name
    logger.info("Writing %d feature(s) to %s", len(gdf), out_path)
    gdf.to_file(out_path, driver="GeoJSON")
    logger.info("Done.")


if __name__ == "__main__":
    main()