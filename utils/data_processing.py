import pandas as pd


def co2_data_filter(df_input, columns, na_columns):
    """
    Filters the data frame to the necessary columns and deletes those rows
    that do not contain any information or belong to Antarctica.

    :param df_input: original data from Our World in Data
    :param columns: Defined columns to keep
    :param na_columns: Columns where no na-values may exist
    :return: edited dataframe
    """
    df = df_input[(df_input['year'] >= 1990) & (df_input['year'] <= 2020)][columns]

    df = df.dropna(subset=na_columns)

    df = df[df['country'] != 'Antarctica']

    return df


def co2_data_add_continents(df_input, df_continent, drop_cc_combination):
    """
    Adds new column 'continent' based on given assignment in df_continent to df.
    Additionally, deletes that combination of countries that have been assigned to two continents.
    The continent that is economically subordinate is deleted

    :param df_input: dataframe with iso_code for mapping
    :param df_continent: dataframe containing iso_code and corresponding continent
    :param drop_cc_combination: Dictionary of country and continent to be deleted.
    :return: edited dataframe
    """
    df = pd.merge(df_input, df_continent, on='iso_code', how='left')

    for continent, countries in drop_cc_combination.items():
        for country in countries:
            df = df.drop(df[(df['continent'] == continent) & (df['country'] == country)].index)

    return df


def co2_data_add_groupings(df_input, df_economies, df_eu, df_oecd):
    """
    adds new columns
    - 'Income group'
    - 'Region'
    - 'EU member' and
    - 'OECD member'
    based on given assignment in df_economies to df

    :param df_input: dataframe with iso_code for mapping
    :param df_economies: dataframe containing iso_code and corresponding region and income group
    :param df_eu: dataframe containing iso_code and corresponding EU membership
    :param df_oecd: dataframe containing iso_code and corresponding OECD membership
    :return: edited dataframe
    """

    df = pd.merge(df_input, df_economies, on='iso_code', how='left')
    df = pd.merge(df, df_eu, on='iso_code', how='left')
    df = pd.merge(df, df_oecd, on='iso_code', how='left')

    df = df.fillna({'EU member': 'no', 'OECD member': 'no'})

    return df
