import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


def extract_lat_lon(coordinates):
    """
    Extracts rounded latitude and longitude from coordinates in comma separated string format.

    :param coordinates: coordinates, first latitude, then longitude, in comma separated string format
    :return: rounded latitude, rounded longitude
    """
    # extract latitude and longitude
    latitude, longitude = map(float, coordinates.split(', '))

    # to find the given coordinates in the dataset, they must match the criteria (= odd and integer)
    rounded_lat = int(latitude)
    rounded_lat += 1 if rounded_lat % 2 == 0 else 0

    rounded_lon = int(longitude)
    rounded_lon += 1 if rounded_lon % 2 == 0 else 0

    return rounded_lat, rounded_lon


def find_location(coordinates):
    """
    Extracts location (city, country) from coordinates in comma separated string format.

    :param coordinates: coordinates, first latitude, then longitude, in comma separated string format
    :return: location (city, country), message in case of error, status (error / no error)
    """
    geolocator = Nominatim(user_agent="myGeocoder")

    # input check for valid latitude and longitude values
    try:
        latitude, longitude = map(float, coordinates.split(', '))

    # raise error if input is wrong type
    except ValueError:
        message = 'Invalid input!'
        status = 'error'

        return None, status, message

    # in case of valid values
    if (-90 <= latitude <= 90) and (-180 <= longitude <= 180):
        # check if city and state can be determined (i.e. not possible for ocean coordinates)
        try:
            location = geolocator.reverse((latitude, longitude), language='en')

        # other reasons for no determination
        except (GeocoderTimedOut, GeocoderUnavailable):
            message = 'No geocoding_service or lasts too long!'
            status = 'error'
            return None, status, message

        if location is None:
            message = 'Coordinates not useful for location!'
            status = 'error'

            return location, status, message

        else:
            # extract complete address
            address = location.raw['address']

            # composition of location
            location_city = address.get('city', address.get('town', address.get('village', 'unknown')))
            location_country = address.get('country', 'unknown')
            location = f'{location_city}, {location_country}'

            message = ''
            status = 'no_error'

            return location, status, message

    else:
        # error text for input box
        message = 'Invalid values for latitude and / or longitude!'

        # (re-) composition style of input  in case of error
        status = 'error'

        return None, status, message


def find_coordinates(location):
    """
    Extracts coordinates from location (city, country) in comma separated string format.

    :param location: location (city, country) in comma separated string format
    :return: coordinates (latitude, longitude), message in case of error, status (error / no error)
    """
    geolocator = Nominatim(user_agent="myGeocoder")

    # check if coordinates can be determined
    try:
        coordinates = geolocator.geocode(location)
        if coordinates is None:
            message = 'No valid location!'
            status = 'error'
            return coordinates, status, message

    # other reasons for no determination
    except (GeocoderTimedOut, GeocoderUnavailable):
        message = 'No geocoding service available or it lasts too long!'
        status = 'error'
        return None, status, message

    message = ''
    status = 'no_error'

    return coordinates, status, message


def add_marker(fig, latitude, longitude):
    """
    Adds marker at given coordination points

    :param fig: fig to which marker is added
    :param latitude: given latitude
    :param longitude: given longitude
    :return: no return
    """
    fig.add_trace(
        go.Scattergeo(
            lat=[latitude], lon=[longitude],
            mode='markers', showlegend=False,
            marker=dict(size=10, color='black', symbol='x'),
            hoverinfo='none',
            customdata=None
        )
    )

    return fig


def add_country_shape(fig, gdf, location, countryname_changes):
    """
    Adds shape of country (location) to choropleth map based on geojson data

    :param fig: fig to which shape is added
    :param gdf: geojson with country (geo-) informationen
    :param location: location (city, country) in comma separated format
    :param countryname_changes:
    :return: no return
    """
    country = location.split(', ')[-1]
    if country in countryname_changes.keys():
        country = countryname_changes[country]

    gdf_country = gdf[gdf['ADMIN'] == country]

    if not gdf_country.empty:
        fig.add_trace(go.Choropleth(
            geojson=gdf_country.geometry.__geo_interface__,
            locations=gdf_country.index,
            z=[1],  # Konstante Farbe, da wir nur die Grenzen anzeigen möchten
            colorscale="Viridis",
            showscale=False,
            marker_line_width=2,  # Grenzlinienbreite
            hoverinfo='none',
            customdata=None
        ))

    return fig


def extract_min_max_mean_anomalies(df_input):
    """
    Calculates the minimum, maximum and average values of temperature anomalies of given dataframe

    :param df_input: Given dataframe
    :return: respective dataframes for minimum, maximum and average values
    """
    # empty dataframe with month numbers (1-12) as base dataframe
    all_months = pd.DataFrame({'Month': range(1, 13)})

    # extract min, max and mean values per month
    df_min = df_input.groupby('Month')['Anomaly'].min()
    df_max = df_input.groupby('Month')['Anomaly'].max()
    df_mean = df_input.groupby('Month')['Anomaly'].mean()

    # reset index for merge process
    df_min = df_min.reset_index()
    df_max = df_max.reset_index()
    df_mean = df_mean.reset_index()

    # merge extracted data with base dataframe
    df_min = pd.merge(all_months, df_min, how='left', on='Month')
    df_max = pd.merge(all_months, df_max, how='left', on='Month')
    df_mean = pd.merge(all_months, df_mean, how='left', on='Month')

    # add type of values
    df_min['Type'] = 'absolute global min values in given year'
    df_max['Type'] = 'absolute global max values in given year'
    df_mean['Type'] = 'global mean values in given year'

    return df_min, df_max, df_mean


def create_polar_line_figure(df_input, min_value, max_value, months):
    """
    Creates polar line figure based on given dataframe, minimum and maximum values for plot range

    :param df_input: given dataframe
    :param min_value: minimum value for plot
    :param max_value: maximum value for plot
    :param months: list of months for legend
    :return: polar line figure
    """
    # define color map for line_polar
    color_map = {
        'absolute global max values in given year': 'red',
        'absolute global min values in given year': 'blue',
        'global mean values in given year': 'green'
    }

    # closed lines only if values for december is in dataset
    line_close = not pd.isna(df_input['Anomaly'].iloc[-1])

    # visualization of global temperature anomaly extreme values on a line polar plot
    fig = px.line_polar(df_input, r='Anomaly', theta='Month', color='Type', line_shape='spline', line_close=line_close,
                        range_r=[int(min_value)-1, int(max_value)+1], color_discrete_map=color_map,
                        hover_name='Month', hover_data={'Type': False, 'Month': False},
                        labels={'Anomaly': 'Anomaly in °C'})

    # change trace for reference comparison
    for trace in fig.data:
        if trace.name == 'reference values':
            trace.line = dict(dash='dash', color='black')
        else:
            trace.opacity = 0.5

    fig = go.Figure(fig)

    # define trace properties of plot background
    trace_properties = [
        (min_value * 0.8, 'toself', 'purple'),
        (min_value * 0.6, 'tonext', 'darkblue'),
        (min_value * 0.4, 'tonext', 'blue'),
        (min_value * 0.2, 'tonext', 'lightblue'),
        (min_value * 0.05, 'tonext', 'lightgreen'),
        (max_value * 0.05, 'tonext', 'white'),
        (max_value * 0.2, 'tonext', 'yellow'),
        (max_value * 0.4, 'tonext', 'orange'),
        (max_value * 0.6, 'tonext', 'darkorange'),
        (max_value * 0.8, 'tonext', 'red'),
        (max_value + 1, 'tonext', 'darkred')
    ]

    # add traces to the figure by iterating through the list of properties
    for r_value, fill_type, fill_color in trace_properties:
        fig.add_trace(go.Scatterpolar(
            name=fill_color,
            r=[r_value for _ in range(13)],
            theta=[month for month in months],
            fill=fill_type,
            fillcolor=fill_color,
            mode='none',
            opacity=0.2,
            showlegend=False,
            hoverinfo='none'
        ))

    # reading and splitting the traces into two lists: One for the traces to be moved and one for the rest
    traces = fig.data
    traces_to_send_to_back = [trace for trace in traces if 'values' in trace.name]
    other_traces = [trace for trace in traces if 'values' not in trace.name]

    # combining the two lists so that the traces to be moved come all the way to the end
    new_traces = other_traces + traces_to_send_to_back
    fig.data = new_traces

    # legend to the left
    fig.update_layout(legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=0))

    return fig


def create_line_figure(df_input, min_value, max_value):
    """
    Creates line figure based on given dataframe, minimum and maximum values for plot range

    :param df_input: given dataframe
    :param min_value: minimum value for plot
    :param max_value: maximum value for plot
    :return: line figure
    """
    # visualization of global temperature anomaly mean values on a line plot
    fig = px.line(df_input, x='Year', y='Anomaly', range_y=[min_value-min_value*0.2, 0.2*max_value+max_value],
                  color='Type', color_discrete_map={'global mean values': 'green'}, line_shape='spline',
                  labels={'Anomaly': 'Anomaly in °C'})

    # change trace for reference comparison
    for trace in fig.data:
        if trace.name == 'reference values':
            trace.line = dict(dash='dash', color='black')
        else:
            trace.opacity = 0.5

    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(hovermode="x unified")

    # Add area shading for values above and below zero
    fig.add_hrect(y0=0.8 * max_value, y1=0.2*max_value+max_value, line_width=0, fillcolor="darkred", opacity=0.2)
    fig.add_hrect(y0=0.6 * max_value, y1=0.8 * max_value, line_width=0, fillcolor="red", opacity=0.2)
    fig.add_hrect(y0=0.4 * max_value, y1=0.6 * max_value, line_width=0, fillcolor="darkorange", opacity=0.2)
    fig.add_hrect(y0=0.2 * max_value, y1=0.4 * max_value, line_width=0, fillcolor="orange", opacity=0.2)
    fig.add_hrect(y0=0.05 * max_value, y1=0.2 * max_value, line_width=0, fillcolor="yellow", opacity=0.2)
    fig.add_hrect(y0=0.05 * min_value, y1=0.05 * max_value, line_width=0, fillcolor="white", opacity=0.2)
    fig.add_hrect(y0=0.2 * min_value, y1=0.05 * min_value, line_width=0, fillcolor="lightgreen", opacity=0.2)
    fig.add_hrect(y0=0.4 * min_value, y1=0.2 * min_value, line_width=0, fillcolor="lightblue", opacity=0.2)
    fig.add_hrect(y0=0.6 * min_value, y1=0.4 * min_value, line_width=0, fillcolor="blue", opacity=0.2)
    fig.add_hrect(y0=0.8 * min_value, y1=0.6 * min_value, line_width=0, fillcolor="darkblue", opacity=0.2)
    fig.add_hrect(y0=min_value-min_value*0.2, y1=0.8 * min_value, line_width=0, fillcolor="purple", opacity=0.2)

    return fig


def group_df(df_input, columns, grouping_criteria, location):
    """
    Groups given dataframe according to grouping criteria.
    Adds data of the country if given

    :param df_input: given dataframe
    :param columns: Required columns of the data frame
    :param grouping_criteria: Column by which the dataframe is grouped
    :param location: location (city, country) in comma separated string format
    :return: grouped dataframe
    """
    # only required columns (append columns list by grouping column)
    columns.add(grouping_criteria)
    columns = list(columns)
    df = df_input[columns]
    df = df.dropna(subset=grouping_criteria)

    df = df.groupby([grouping_criteria, 'year']).sum(numeric_only=True)
    df['consumption_co2_per_capita'] = df['consumption_co2']*1000000 / df['population']
    df = df.reset_index()
    df = df.sort_values(['year', 'consumption_co2', 'consumption_co2_per_capita'], ascending=[True, False, False])

    if location != '':
        location = location.split(', ')[1]
        df_location = df_input[df_input['country'] == location][['year', 'population', 'consumption_co2',
                                                                 'consumption_co2_per_capita', grouping_criteria]]
        df_location[grouping_criteria] = location
        df = pd.concat([df, df_location])

    return df


def filter_df(df_input, columns, filter_column, filter_criteria, location):
    """
    Filters dataframe according to filter criteria.

    :param df_input: given dataframe
    :param columns: Required columns of the data frame
    :param filter_column: Column on which the filter is applied
    :param filter_criteria: Filter criteria
    :param location: location (city, country) in comma separated string format
    :return: filtered dataframe
    """
    columns = list(columns)

    # only required columns
    if isinstance(filter_criteria, list):
        df = df_input[df_input[filter_column].isin(filter_criteria)][columns]
    else:
        df = df_input[df_input[filter_column] == filter_criteria][columns]

    df = df.sort_values(['year', 'consumption_co2', 'consumption_co2_per_capita'], ascending=[True, False, False])

    if location != '':
        location = location.split(', ')[1]
        location_present = df['country'].str.contains(location).any()
        if not location_present:
            df_location = df_input[df_input['country'] == location][columns]
            df = pd.concat([df, df_location])

    return df


def xy_filter_df(df_input, merge_column, x_year, y_year):
    """
    Splits given dataframe into two dataframes with filtered years and merges back together for having
    two separated columns according to 'consumption_co2_per_capita'.

    :param df_input: given dataframe
    :param merge_column: column on which dataframes are merged back together
    :param x_year: year (integer) for filtering first dataframe.
    :param y_year: year (integer) for filtering second dataframe.
    :return: dataframe with two columns 'consumption_co2_per_capita' for x and y
    """
    df_x = df_input[df_input['year'] == x_year] \
        .rename(columns={'consumption_co2_per_capita': 'consumption_co2_per_capita_x_year'}) \
        .drop('year', axis=1)

    df_y = df_input[df_input['year'] == y_year] \
        .rename(columns={'consumption_co2_per_capita': 'consumption_co2_per_capita_y_year'}) \
        .drop('year', axis=1)

    df = pd.merge(df_x, df_y, on=[merge_column])
    df['mean_population'] = (df['population_x'] + df['population_y']) / 2

    return df


def create_co2_consumption_fig(df, color, left_year, right_year):
    """
    Creates CO2 consumption line figure color-grouped by specific column.
    Adds background shape based on specific years (x-axis).

    :param df: given dataframe.
    :param color: Column on which the color scheme is based.
    :param left_year: Left year (x-axis) for color background.
    :param right_year: Right year (x-axis) for color background
    :return: line figure
    """
    # extract maximum value
    max_value = df['consumption_co2'].max()

    # create figure
    fig = px.line(df, x='year', y='consumption_co2', color=color,
                  labels={'consumption_co2': 'CO₂ Consumption in million tonnes', 'year': 'Year'})

    fig.update_xaxes(gridcolor="rgba(0,0,0,0.5)", gridwidth=0.5)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0.5)", gridwidth=0.5, range=[0-max_value*0.05, max_value*1.05])
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    fig.update_layout(plot_bgcolor='white', hovermode='x')

    # adding line marking Kyoto
    fig.add_trace(
        go.Scatter(x=[1997, 1997], y=[0, max_value], hoverinfo='skip',
                   line=dict(color='red', dash='dash'), name='Kyoto 1997', mode='lines')
    )

    # adding line marking Paris
    fig.add_trace(
        go.Scatter(x=[2015, 2015], y=[0, max_value], hoverinfo='skip',
                   line=dict(color='green', dash='dash'), name='Paris 2015', mode='lines')
    )

    # adding shape marking comparing years
    fig.add_shape(
        go.layout.Shape(
            type="rect",
            xref="x",
            yref="paper",
            x0=left_year,
            y0=0,
            x1=right_year,
            y1=1,
            fillcolor="lightgray",
            opacity=0.5,
            layer="below",
            line_width=0
        )
    )

    return fig


def create_co2_comparison_fig(df, color, x_year, y_year):
    """
    Creates CO2 comparison scatter figure color-grouped by specific column.
    Adds background shape for consumptions threshold.

    :param df: Given dataframe.
    :param color: Column on which the color scheme is based.
    :param x_year: Year to be added to x-axis label
    :param y_year: Year to be added to y-axis label
    :return: scatter figure
    """
    max_value = df[['consumption_co2_per_capita_x_year', 'consumption_co2_per_capita_y_year']].values.max()

    fig = px.scatter(df, color=color, hover_name=color, size='mean_population', size_max=42,
                     x='consumption_co2_per_capita_x_year',
                     y='consumption_co2_per_capita_y_year',
                     labels={'consumption_co2_per_capita_x_year': f'CO₂ consumption in tonnes per capita in {x_year}',
                             'consumption_co2_per_capita_y_year': f'CO₂ consumption in tonnes per capita in {y_year}',
                             'mean_population': f'Population'},
                     hover_data={color: False, 'mean_population': ':,.2f',
                                 'consumption_co2_per_capita_x_year': False,
                                 'consumption_co2_per_capita_y_year': False})

    fig.update_layout(legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=0),
                      plot_bgcolor='white',
                      shapes=[
                          dict(
                              type="rect",
                              x0=0,
                              x1=1.6,
                              y0=0,
                              y1=1.6,
                              xref="x",
                              yref="y",
                              fillcolor="rgba(0, 255, 0, 0.5)",
                              line=dict(width=0),
                              layer="below",
                              opacity=0.2
                          ),
                          dict(
                              type="rect",
                              x0=1.6,
                              x1=max_value * 1.1,
                              y0=0,
                              y1=max_value * 1.1,
                              xref="x",
                              yref="y",
                              fillcolor="rgba(255, 0, 0, 0.5)",
                              line=dict(width=0),
                              layer="below",
                              opacity=0.2
                          ),
                          dict(
                              type="rect",
                              x0=0,
                              x1=1.6,
                              y0=1.6,
                              y1=max_value * 1.1,
                              xref="x",
                              yref="y",
                              fillcolor="rgba(255, 0, 0, 0.5)",
                              line=dict(width=0),
                              layer="below",
                              opacity=0.2
                          ),
                          dict(
                              type="line",
                              x0=0,
                              y0=0,
                              x1=max_value*1.1,
                              y1=max_value*1.1,
                              line=dict(color="black", width=2),
                              layer="below",
                              opacity=0.5
                          )
                      ])

    fig.update_xaxes(gridcolor="rgba(0,0,0,0.5)", gridwidth=0.2,
                     tickvals=np.arange(0, max_value + 1, step=2),
                     range=[0-max_value*0.05, max_value*1.1],
                     showspikes=True)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0.5)", gridwidth=0.2,
                     tickvals=np.arange(0, max_value + 1, step=2),
                     range=[0-max_value*0.05, max_value*1.1], side="right",
                     showspikes=True)

    return fig
