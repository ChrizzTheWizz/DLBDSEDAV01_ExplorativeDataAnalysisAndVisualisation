from pathlib import Path
import yaml
import pandas as pd
import geopandas as gpd
import netCDF4
from datetime import timedelta, date


def read_config_file():
    """
    ready config file containing
    - filepaths,
    - data information (i.e. columns of dataframe) and
    - dash information (i.e. default styles, options for dropdown-lists)

    :return: configuration data
    """
    file = Path('./config/config.yaml')
    if file.exists():
        with open(file, 'r') as config_file:
            config_data = yaml.safe_load(config_file)
        return config_data
    else:
        raise FileNotFoundError


def update_config_file(data):
    file = Path('./config/config.yaml')
    with open(file, 'w') as config_file:
        yaml.dump(data, config_file, default_flow_style=False)


def read_content_file(filepath):
    """
    reads content (headlines, text) of dash

    :param filepath: filepath to content file
    :return: content data
    """
    file = Path(filepath)
    if file.exists():
        with open(file, 'r', encoding='utf-8') as content_file:
            content_data = yaml.safe_load(content_file)
        return content_data
    else:
        raise FileNotFoundError


def read_geo_data(filepath):
    """
    reads geojson retrieved from https://datahub.io/core/geo-countries

    :param filepath: filepath to geojson
    :return: geojson data of countries
    """
    file = Path(filepath)
    if file.exists():
        geojson_data = gpd.read_file(file)
        return geojson_data
    else:
        raise FileNotFoundError


def read_nasa_file(nc_filepath, json_filepath):
    """
    reads and if not yet processed filters Gridded Monthly Temperature Anomaly Data NetCDF-File retrieved from
    https://data.giss.nasa.gov/gistemp/

    if NetCDF-File already filtered only json-File is read

    :param nc_filepath: filepath to NetCDF-File
    :param json_filepath: filepath to JSON-File
    :return: Gridded Monthly Temperature Anomaly Data as Pandas Dataframe
    """
    nc_file = Path(nc_filepath)
    json_file = Path(json_filepath)
    if json_file.exists():
        df = pd.read_json(json_file)
        return df
    elif nc_file.exists():
        def days_to_date(days_since_1800):
            start_date = date(1800, 1, 1)
            target_date = start_date + timedelta(days=days_since_1800)
            date_str = target_date.strftime('%Y-%m')
            return date_str

        # read NetCDF-File
        nc_dataset = netCDF4.Dataset(nc_file)

        # create empty dataframe with corresponding columns
        df = pd.DataFrame(columns=['Longitude', 'Latitude', 'Anomaly', 'Period'])

        # extract data from NetCDF-File
        lat = nc_dataset.variables['lat'][:]
        lon = nc_dataset.variables['lon'][:]

        for i, time in enumerate(nc_dataset.variables['time']):
            datum = days_to_date(int(time))
            if int(datum[:4]) < 1990:
                continue

            temp_anomaly = nc_dataset.variables['tempanomaly'][i, :, :]

            df_temp_anomaly = pd.DataFrame(temp_anomaly, columns=lon, index=lat)

            df_temp_anomaly_melted = df_temp_anomaly.reset_index().melt(id_vars=['index'],
                                                                        var_name='Longitude',
                                                                        value_name='Anomaly')

            df_temp_anomaly_melted = df_temp_anomaly_melted.rename(columns={'index': 'Latitude'})

            df_temp_anomaly_melted['Period'] = datum
            df_temp_anomaly_melted['Year'] = datum.split('-')[0]
            df_temp_anomaly_melted['Month'] = datum.split('-')[1]

            df = pd.concat([df, df_temp_anomaly_melted])

        df.reset_index(drop=True, inplace=True)
        df = df.sort_values(by='Period', ascending=True)
        df.to_json(json_file)
        df = pd.read_json(json_file)

        return df
    else:
        raise FileNotFoundError


def read_co2_data(filepath):
    """
    reads CSV-File about CO2-Emissions from "Our World in Dat" retrieved from https://github.com/owid

    :param filepath: filepath to CSV-File
    :return: CO2-Data as Pandas Dataframe
    """
    file = Path(filepath)
    if file.exists():
        df = pd.read_csv(file)
        return df
    else:
        raise FileNotFoundError


def read_co2_data_codebook(filepath):
    """
    reads CSV-File about co2-column explanation (=Codebook) from "Our World in Dat"
    retrieved from https://github.com/owid

    :param filepath: filepath to CSV-File
    :return: CO2-Data-Codebook as Pandas Dataframe
    """
    file = Path(filepath)
    if file.exists():
        df = pd.read_csv(file)
        df = df.set_index('column')
        return df
    else:
        raise FileNotFoundError


def read_cc_mapping(filepath):
    """
    read CSV-File to assign continents (North- and South America combined) to countries retrieved from
    https://gist.github.com/stevewithington/20a69c0b6d2ff846ea5d35e5fc47f26c

    :param filepath: filepath to CSV-File
    :return: ISO-Code - Continent Pandas Dataframe
    """
    file = Path(filepath)
    if file.exists():
        df = pd.read_csv(file, usecols=['Continent_Name', 'Three_Letter_Country_Code'])
        df.rename(columns={'Continent_Name': 'continent', 'Three_Letter_Country_Code': 'iso_code'}, inplace=True)

        df.dropna(subset=['iso_code'], inplace=True)
        df['continent'] = df['continent'].replace(['North America', 'South America'], 'America')

        return df
    else:
        raise FileNotFoundError


def read_country_groupings(filepath):
    """
    reads XLSX-File file for classification of countries into groups
    https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups

    :param filepath: filepath to XLSX-File
    :return: ISO-Code - Grouping Pandas Dataframe
    """
    file = Path(filepath)
    if file.exists():
        df_economies = pd.read_excel(file, sheet_name='List of economies', usecols=['Code', 'Region', 'Income group'])
        df_economies = df_economies.dropna(subset=['Region'])
        df_economies = df_economies.rename(columns={'Code': 'iso_code'})

        df_groups = pd.read_excel(file, sheet_name='Groups', usecols=['GroupName', 'CountryCode'])
        df_groups = df_groups.rename(columns={'CountryCode': 'iso_code'})

        df_eu = df_groups[df_groups['GroupName'] == 'European Union']
        df_eu = df_eu.rename(columns={'GroupName': 'EU member'})
        df_eu['EU member'] = 'yes'

        df_oecd = df_groups[df_groups['GroupName'] == 'OECD members']
        df_oecd = df_oecd.rename(columns={'GroupName': 'OECD member'})
        df_oecd['OECD member'] = 'yes'

        return df_economies, df_eu, df_oecd
    else:
        raise FileNotFoundError
