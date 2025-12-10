"""
Setup script for AUS Land Clearing project
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aus_land_clearing",
    version="0.1.0",
    author="AUS Land Clearing Team",
    description="Story-driven visualisations of land clearing across eastern Australia",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HMB3/AUS_Land_Clearing",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "xarray>=0.19.0",
        "rasterio>=1.2.0",
        "geopandas>=0.9.0",
        "matplotlib>=3.4.0",
    ],
)
