# Course: Explorative Data Analysis and Visualization
# Interactive visualizations based on geo-spatial data according global temperature anomalies and co² consumption

## Table of Contents
1. [About the project](#About-the-project)
2. [Requirements](#Requirements)
3. [Installation](#Installation)
4. [Usage / How to](#Usage-/-How-to)
5. [Contributing](#Contributing)


## About the project
Based on the GISS Surface Temperature Analysis (GISTEMP v4) provided by NASA on the one hand and the data on CO² emissions, consumption and impact on global temperatures provided by Our World in Data on the other hand, this project serves the interactive visualization of those data with the framework Dash.
The aim is to raise users' awareness of global warming by preparing and visualizing data for the period 1990-2020, during which a steady increase can be observed despite the climate conferences that have taken place (Kyoto 1997 & Paris 2015).

IMPORTANT:
This app was developed as part of a case-study course for my Data Science degree and contains the basic requirements according to the assignment. Further development is not planned.

## Requirements

**General:** 
This app was written in Python. Make sure you have Python 3.8+ installed on your device. 
You can download the latest version of Python [here](https://www.python.org/downloads/). 

**Packages:**
* [dash](https://dash.plotly.com) (install via "pip install dash")
* [plotly](https://plotly.com/python/) (install via "pip install plotly)
* [numpy](https://numpy.org) (install via "pip install numpy")
* [pandas](https://pandas.pydata.org/about/index.html) (install via "pip install pandas")
* [geopandas](https://geopandas.org/en/stable/) (install via "pip install geopandas")
* [geopy](https://geopy.readthedocs.io/en/stable/) (install via "pip install geopy")* 
* [pathlib](https://docs.python.org/3/library/pathlib.html) (install via "pip install pathlib")
* [yaml](https://python.land/data-processing/python-yaml) (install via "pip install yaml")* 
* [netCDF4](https://unidata.github.io/netcdf4-python/) (install via "pip install netCDF4")
* [datetime](https://docs.python.org/3/library/datetime.html) (install via "pip install datetime") 

**Data:**

The following files are already in the current repository under "/data/". 
It is recommended that you use them. However, the current data can also be obtained as follows:

* [GISS Surface Temperature Analysis (GISTEMP v4)](https://data.giss.nasa.gov/pub/gistemp/gistemp1200_GHCNv4_ERSSTv5.nc.gz)
* [CO2 and Greenhouse Gas Emissions](https://github.com/owid/co2-data/blob/master/owid-co2-data.csv)
* [CO2 and Greenhouse Gas Emissions Codebook](https://github.com/owid/co2-data/blob/master/owid-co2-codebook.csv)
* [Country shapes (geo data)](https://datahub.io/core/geo-countries/r/countries.geojson)
* [Country to Continent Mapping](https://gist.github.com/stevewithington/20a69c0b6d2ff846ea5d35e5fc47f26c)
* [World Bank Country and Lending Groups](https://datacatalogfiles.worldbank.org/ddh-published/0037712/DR0090755/CLASS.xlsx)


## Installation

**How To:**<br>
The easiest way to use this app is to download the complete repository.
The data can be downloaded separately as described above. However, the following data must be downloaded:

/main.py
/assets/header_bg.png
/config/config.yaml
/data/content.yaml
/utils/__init__.py
/utils/dash_processing.py
/utils/data_loading.py
/utils/data_processing.py


## Usage / How to

You only have to run main.py. Make sure that you have downloaded the required data - either via this repository or the links provided here.

## Contributing 
With reference to the fact that this app was created in the course of my studies and I am therefore in a constant learning process, I am happy to receive any feedback.
So please feel free to contribute pull requests or create issues for bugs and feature requests.
