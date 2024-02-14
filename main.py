# import interactivity-framework dash and needed components
from dash import Dash, dcc, Output, Input, State, html, dash_table, no_update
import dash_bootstrap_components as dbc

from utils.data_loading import *
from utils.data_processing import *
from utils.dash_processing import *

# ----------------------------------------------------------------------------------------------------------------------

config = read_config_file()

# ----------------------------------------------------------------------------------------------------------------------
# EXTRACT DEFAULT VALUES
default_height = int(config['dash_information']['general']['default_padding_value'])
default_color = config['dash_information']['general']['default_color_hex']
default_table_style = config['dash_information']['general']['default_table_style']

# ----------------------------------------------------------------------------------------------------------------------
# EXTRACT FILEPATHS
filepath_content_data = config['filepaths']['content_data']
filepath_geo_data = config['filepaths']['geo_data']
filepath_nasa_nc_data = config['filepaths']['nasa_nc_data']
filepath_nasa_json_data = config['filepaths']['nasa_json_data']
filepath_owid_co2_data = config['filepaths']['owid_co2_data']
filepath_owid_co2_codebook = config['filepaths']['owid_co2_codebook']
filepath_country_continent_mappings = config['filepaths']['country_continent_mappings']
filepath_country_grouping_mappings = config['filepaths']['country_grouping_mappings']

# ----------------------------------------------------------------------------------------------------------------------
# EXTRACT DASHBOARD CONTENT
content = read_content_file(filepath_content_data)

# ----------------------------------------------------------------------------------------------------------------------
# LOAD GEOJSON FOR COUNTRY BORDERS
gdf_countries = read_geo_data(filepath_geo_data)

# ----------------------------------------------------------------------------------------------------------------------
# LOAD GLOBAL TEMPERATURE ANOMALIES: NASA FILE (original: nc; edited: json)
df_anomaly_heatmap = read_nasa_file(filepath_nasa_nc_data, filepath_nasa_json_data)
giss_data_latest_date = df_anomaly_heatmap['Period'].max()

# ----------------------------------------------------------------------------------------------------------------------
# LOAD, EDIT AND ENRICH GLOBAL CO2 DATA: OWID (Our World In Data)
co2_data_columns = config['data_information']['co2_data_columns']
co2_data_na_columns = config['data_information']['co2_data_na_columns']
co2_data_drop_cc_combinations = config['data_information']['co2_data_drop_cc_combinations']

df_cc_mapping = read_cc_mapping(filepath_country_continent_mappings)
df_countries_by_income, df_countries_eu, df_countries_oecd = read_country_groupings(filepath_country_grouping_mappings)

df_co2_data = read_co2_data(filepath_owid_co2_data)
df_co2_data = co2_data_filter(df_co2_data, co2_data_columns, co2_data_na_columns)
df_co2_data = co2_data_add_continents(df_co2_data, df_cc_mapping, co2_data_drop_cc_combinations)
df_co2_data = co2_data_add_groupings(df_co2_data, df_countries_by_income, df_countries_eu, df_countries_oecd)

# ----------------------------------------------------------------------------------------------------------------------
# LOAD CO2 DATA CODEBOOK: OWID (Our World In Data)
df_co2_codebook = read_co2_data_codebook(filepath_owid_co2_codebook)
data_columns_information = config['data_columns_information']
for data_column in data_columns_information:
    if data_column['data_source_column'] == 'CO2 and Greenhouse Gas Emissions (Our World in Data)':
        data_column['data_description'] = df_co2_codebook.loc[data_column['data_column'], 'description']

# ----------------------------------------------------------------------------------------------------------------------

# Create the Dash application
app = Dash(__name__, external_stylesheets=[dbc.themes.UNITED], title='Explorative Analysis of clima crisis')

# Definiere das Layout
app.layout = dbc.Container(
    html.Div([

        # --------------------------------------------------------------------------------------------------------------
        # Preliminary information
        dbc.Row(
            dbc.Col([
                html.Div('Preliminary information'),
                dcc.Checklist(id='checkbox_show_again', options=[{'label': "Don't show again", 'value': 'disable'}]),
                html.Button('Close', id='hide_button'),
                ],
                width=12,
            ), style={'opacity': 1, 'transition': 'opacity 0.5s'},
            id='preliminary_information'),

        # --------------------------------------------------------------------------------------------------------------
        # HEADLINE WITH BACKGROUND IMAGE
        dbc.Row(
            dbc.Col(
                html.Div(children=[
                    html.H1(children=content['00_header']['title'],
                            id='00_header_title',
                            style={'color': 'white', 'text-align': 'center'}),
                    html.H4(children=content['00_header']['subtitle'],
                            id='00_header_subtitle',
                            style={'color': 'white', 'text-align': 'center',
                                   'paddingTop': default_height, 'paddingBottom': default_height})
                ], style={'background-image': 'url(/assets/header_bg.png)',
                          'background-repeat': 'no-repeat',
                          'background-size': 'cover',
                          'height': '30vh',
                          'display': 'flex',
                          'flex-direction': 'column',
                          'justify-content': 'flex-end'}),
                width=12),
            id='00_header'),

        # --------------------------------------------------------------------------------------------------------------
        # 00 NAVIGATION LINKS AND REFERENCE INPUT
        dbc.Row([
            # 00.1 NAVIGATION LINKS
            dbc.Row([
                dbc.Col(
                    html.Div(),
                    width=1),

                dbc.Col(
                    html.Div([
                        html.A('Introduction', href='#00_header',
                               id='00_link', className='nav-link', n_clicks=0),
                        html.A('Global heatmap', href='#01_global_temperature_anomalies',
                               id='01_link', className='nav-link', n_clicks=0),
                        html.A('Temperature anomalies', href='#02_comparison_temperature_anomalies',
                               id='02_link', className='nav-link', n_clicks=0),
                        html.A('CO₂ impact', href='#03_co2_impact_on_temperature',
                               id='03_link', className='nav-link', n_clicks=0),
                        html.A('CO₂ consumption', href='#04_global_co2_consumption',
                               id='04_link', className='nav-link', n_clicks=0),
                        html.A('Data & Information', href='#05_data_and_information',
                               id='05_link', className='nav-link', n_clicks=0),
                    ], className='nav d-flex justify-content-between'),
                    width=10),

                dbc.Col(
                    html.Div(),
                    width=1),
            ], style={'backgroundColor': '#FFFFFF', 'height': 35, 'fontSize': '1.125rem', 'font-weight': 'bold'}),

            # 00.2 SEPARATION LINE
            dbc.Row(
                dbc.Col(
                    html.Hr(style={'height': 5}),
                    width=12, style={'backgroundColor': '#FFFFFF'}
                )
            ),

            # 00.3 REFERENCE HEADLINE
            dbc.Row([
                dbc.Col(
                    html.Div(children=content['00_navigation_and_reference']['reference_intro'],
                             id='00_navigation_and_reference_reference_intro'),
                    width=8, style={'text-align': 'left', 'backgroundColor': '#FFFFFF', 'font-weight': 'bold'}
                ),
                dbc.Col(
                    html.Div(children=content['00_navigation_and_reference']['reference_headline_default'],
                             id='00_output_txt_reference_headline',
                             style={'text-align': 'center', 'font-weight': 'bold'}),
                    width=4
                )
            ], style={'background-color': '#FFFFFF'}),

            # 00.4 INPUT & OUTPUT REFERENCE
            dbc.Row([
                dbc.Col(
                    html.Div([
                        dcc.Input(id='00_input_txt_coordinates', type='text', value='', style={'width': '80%'},
                                  placeholder='Enter Coordinates'),
                        html.Button('Find', id='00_input_btn_reference_coordinates', n_clicks=0)
                    ]),
                    width=4,
                    style={'text-align': 'center', 'backgroundColor': '#FFFFFF'}
                ),

                dbc.Col(
                    html.Div([
                        dcc.Input(id='00_input_txt_location', type='text', value='', style={'width': '80%'},
                                  placeholder='Enter location'),
                        html.Button('Find', id='00_input_btn_reference_location', n_clicks=0)
                    ]),
                    width=4,
                    style={'text-align': 'center', 'backgroundColor': '#FFFFFF'}
                ),

                dbc.Col(
                    html.Div([
                        html.Div(id='00_output_txt_reference_location',
                                 style={'text-align': 'right'})
                    ]),
                    width=2,
                    style={'backgroundColor': '#FFFFFF'}
                ),

                dbc.Col(
                    html.Div([
                        html.Div(id='00_output_txt_reference_coordinates',
                                 style={'text-align': 'right'})
                    ]),
                    width=2
                )
            ], style={'paddingTop': default_height, 'background-color': '#FFFFFF'}),

            # 00.5 SEPARATION LINE
            dbc.Row(
                dbc.Col(
                    html.Hr(style={'height': 5}),
                    width=12, style={'backgroundColor': '#FFFFFF'}
                )
            ),

        ], id='00_navigation_and_reference', className="sticky-top", style={'margin': '0.025rem'}),

        # --------------------------------------------------------------------------------------------------------------
        # 01 INTRODUCTION AND WORLD HEATMAP (GLOBAL TEMPERATURE ANOMALIES)
        dbc.Row([
            # 01.1 INTRODUCTION
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.H5('Introduction'),
                        html.Hr(),
                        html.Div(children=content['01_global_temperature_anomalies']['content_header'],
                                 id='01_global_temperature_anomalies_txt_content',
                                 style={'text-align': 'left', 'paddingTop': default_height}),
                        html.Div(children=content['01_global_temperature_anomalies']['content_description'],
                                 id='01_global_temperature_anomalies_txt_content_description',
                                 style={'text-align': 'left'}),
                    ]),
                    width=12
                )
            ]),

            # 01.2 FILLED SEPARATION LINE
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.Div(style={'background-color': default_color, 'height': default_height}),
                    ]),
                    width=12
                ),

            ], style={'paddingTop': default_height * 2}),

            # 01.3 HEADLINE GLOBAL TEMPERATURE ANOMALIES AND TEXTUAL OUTPUT TEMPERATURE ANOMALY REFERENCE LOCATIONS
            dbc.Row([
                dbc.Col(width=3),

                dbc.Col(
                    html.Div([
                        html.H5(children=f"{content['01_global_temperature_anomalies']['header_figure']} "
                                         f"from {giss_data_latest_date}",
                                id='01_global_temperature_anomalies_header_figure',
                                style={'text-align': 'center', 'font-weight': 'bold'}),
                        html.Div(style={'background-color': default_color, 'height': default_height}),
                        html.Div(children=content['01_global_temperature_anomalies']['reference_temp_anomaly_default'],
                                 id='01_output_txt_reference_temp_anomaly',
                                 style={'text-align': 'center', 'font-weight': 'bold'}),
                        html.Div(children=content['01_global_temperature_anomalies']['figdata_temp_anomaly_default'],
                                 id='01_output_txt_figdata_temp_anomaly',
                                 style={'text-align': 'center', 'font-weight': 'bold'})
                    ]),
                    width=6
                ),

                dbc.Col(width=3)
            ], style={'paddingTop': default_height}),

            # 01.4 FIGURE WORLD HEATMAP (GLOBAL TEMPERATURE ANOMALIES)
            dbc.Row([
                dbc.Col(
                    html.Div([
                        dcc.Graph(id='01_output_fig_global_heatmap_temp_anomalies',
                                  config=config['dash_information']['general']['fig_config'],
                                  style={'height': '60vh'}),
                    ]),
                    width=12
                )

            ]),

            # 01.5 CONCLUSION
            dbc.Row([
                dbc.Col(width=3),

                dbc.Col(
                    html.Div([
                        html.Div(children='Conclusions:', style={'text-align': 'left', 'font-weight': 'bold'}),
                        html.Div(children=content['01_global_temperature_anomalies']['figure_description'],
                                 id='01_global_temperature_anomalies_txt_figure_description',
                                 style={'text-align': 'left', 'paddingTop': default_height}),
                    ]),
                    width=6
                ),

                dbc.Col(width=3)
            ]),
        ], id='01_global_temperature_anomalies'),

        # --------------------------------------------------------------------------------------------------------------
        # 02 DIRECT COMPARISON GLOBAL AND LOCAL TEMPERATURE ANOMALIES
        dbc.Row([
            # 02.1 HEADLINES
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.H5(children=content['02_comparison_temperature_anomalies']['header_left'],
                                id='02_comparison_temperature_anomalies_header_left',
                                style={'text-align': 'center', 'font-weight': 'bold'}),
                        html.Div(style={'background-color': default_color, 'height': default_height}),
                    ]),
                    width=3,
                    style={'align-self': 'end'}
                ),

                dbc.Col(width=6),

                dbc.Col(
                    html.Div([
                        html.H5(children=content['02_comparison_temperature_anomalies']['header_right'],
                                id='02_comparison_temperature_anomalies_header_right',
                                style={'text-align': 'center', 'font-weight': 'bold'}),
                        html.Div(style={'background-color': default_color, 'height': default_height}),
                    ]),
                    width=3,
                    style={'align-self': 'end'}
                ),

            ], style={'height': '25vh'}),

            # 02.2 CHAPTER CONTENT
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.Div(children=content['02_comparison_temperature_anomalies']['content_01'],
                                 id='02_comparison_temperature_anomalies_content_01', style={'text-align': 'center'}),
                        html.Div(children=content['02_comparison_temperature_anomalies']['content_02'],
                                 id='02_comparison_temperature_anomalies_content_02', style={'text-align': 'center'})
                    ]),
                    width=12
                )
            ], style={'paddingTop': default_height * 2}),

            # 02.3 YEAR-SLIDER INPUT
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.Hr(),
                        dcc.Slider(
                            id='02_input_sld_years',
                            min=df_anomaly_heatmap['Year'].min(),
                            max=df_anomaly_heatmap['Year'].max(),
                            value=df_anomaly_heatmap['Year'].min(),
                            marks={str(year): str(year) if year % 5 == 0 else ''
                                   for year in df_anomaly_heatmap['Year'].unique()},
                            step=None
                        ),
                    ]),
                    width=6
                ),

                dbc.Col(width=6),
            ], style={'paddingTop': default_height}),

            # 02.4 FIGURE OUTPUTS
            dbc.Row([
                dbc.Col(
                    html.Div([
                        dcc.Graph(id='02_output_fig_minmax_temp_anomaly',
                                  config=config['dash_information']['general']['fig_config']),
                    ]),
                    width=6
                ),

                dbc.Col(
                    html.Div([
                        dcc.Graph(id='02_output_fig_mean_temp_anomalies',
                                  config=config['dash_information']['general']['fig_config'])
                    ]),
                    width=6
                ),
            ])
        ], id='02_comparison_temperature_anomalies'),

        # --------------------------------------------------------------------------------------------------------------
        # 03 WORLDMAP / TREEMAP IMPACT CO2 TO TEMPERATURE
        dbc.Row([
            # 03.1 HEADLINES AND DESCRIPTION OF CO2 EMISSION IMPACT
            dbc.Row([
                dbc.Col(width=2),

                dbc.Col(
                    html.Div([
                        html.H5(children=content['03_co2_impact_on_temperature']['header'],
                                id='03_co2_impact_on_temperature_header',
                                style={'text-align': 'center', 'font-weight': 'bold'}),
                        html.Div(style={'background-color': default_color, 'height': default_height}),
                    ]),
                    width=8,
                    style={'align-self': 'end'}
                ),

                dbc.Col(width=2),

            ], style={'height': '25vh'}),

            # 03.2 CONCLUSION, TAB AND DROPDOWN INPUT, FIGURE OUTPUTS
            dbc.Row([
                dbc.Col([
                    html.Hr(),
                    html.Div(children=content['03_co2_impact_on_temperature']['content_01'],
                             id='03_co2_impact_on_temperature_txt_content_01',
                             style={'text-align': 'left', 'paddingTop': default_height}),
                    html.Div(children=content['03_co2_impact_on_temperature']['content_02'],
                             id='03_co2_impact_on_temperature_txt_content_02',
                             style={'text-align': 'left', 'paddingTop': default_height})
                ],
                    style={'width': 2, 'paddingTop': default_height * 4}
                ),

                dbc.Col(
                    html.Div([
                        dcc.Tabs(
                            id="03_input_tab_worldmap_treemap", value='world',
                            children=[
                                dcc.Tab(label='Worldmap', value='world'),
                                dcc.Tab(label='Treemap', value='tree')
                            ]),
                        dcc.Dropdown(
                            id='03_input_ddl_treemap_grouping_options',
                            options=config['dash_information']['03_input_ddl_treemap_options'],
                            value='all#continent',
                            placeholder='Select a grouping',
                            style={'opacity': 1, 'transition': 'opacity 0.5s'}
                        ),
                        dcc.Graph(id='03_output_fig_temp_change_co2',
                                  config=config['dash_information']['general']['fig_config'],
                                  style={'height': '50vh'})
                    ]),
                    width=8
                ),

                dbc.Col([
                    html.Hr(),
                    html.Div(children=content['03_co2_impact_on_temperature']['header_fig_ranking'],
                             id='03_co2_impact_on_temperature_header_fig_ranking',
                             style={'text-align': 'left', 'font-weight': 'bold'}),
                    dcc.Graph(id='03_output_fig_temp_change_co2_ranking',
                              config=config['dash_information']['general']['fig_config'])
                ],
                    style={'width': 2, 'paddingTop': default_height * 4}
                ),
            ]),
        ], id='03_co2_impact_on_temperature'),

        # --------------------------------------------------------------------------------------------------------------
        # 04 CO2 CONSUMPTION AND COMPARISON OF CO2 CONSUMPTION
        dbc.Row([
            # 04.1 HEADLINES
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.H5(children=content['04_global_co2_consumption']['header_left'],
                                id='04_global_co2_consumption_header_left',
                                style={'text-align': 'center', 'font-weight': 'bold'}),
                        html.Div(style={'background-color': default_color, 'height': default_height})
                    ]),
                    width=3,
                    style={'align-self': 'end'}
                ),

                dbc.Col(width=6),

                dbc.Col(
                    html.Div([
                        html.H5(children=content['04_global_co2_consumption']['header_right'],
                                id='04_global_co2_consumption_header_right',
                                style={'text-align': 'center', 'font-weight': 'bold'}),
                        html.Div(style={'background-color': default_color, 'height': default_height})
                    ]),
                    width=3,
                    style={'align-self': 'end'}
                ),

            ], style={'height': '25vh'}),

            # 04.2 CHAPTER CONTENT
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.Div(children=content['04_global_co2_consumption']['content_01'],
                                 id='04_global_co2_consumption_content_01', style={'text-align': 'center'}),
                        html.Div(children=content['04_global_co2_consumption']['content_02'],
                                 id='04_global_co2_consumption_content_02', style={'text-align': 'center'}),
                        html.Div(children=content['04_global_co2_consumption']['content_03'],
                                 id='04_global_co2_consumption_content_03', style={'text-align': 'center'}),
                    ]),
                    width=12,
                    style={'paddingTop': default_height * 2}
                )
            ]),

            # 04.2 CHAPTER CONTENT
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.Hr(),
                        dcc.RangeSlider(
                            id='04_input_rsl_years',
                            min=df_co2_data['year'].min(),
                            max=df_co2_data['year'].max(),
                            value=[1997, 2015],
                            marks={str(year): str(year) if year % 2 == 0 else ''
                                   for year in df_co2_data['year'].unique()},
                            step=None
                        ),
                    ]),
                    width=12
                )
            ], style={'paddingTop': default_height}),

            # 04.3 FIGURE OUTPUTS
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.Hr()
                    ]),
                    width=5
                ),

                dbc.Col(
                    html.Div([
                        dcc.Dropdown(
                            id='04_input_ddl_grouping_options',
                            options=config['dash_information']['04_input_ddl_grouping_options'],
                            value='grouping#Income group',
                            placeholder='Select a grouping'
                        ),
                    ]),
                    width=2
                ),

                dbc.Col(
                    html.Div([
                        html.Hr()
                    ]),
                    width=5
                ),
            ]),

            # 04.3 FIGURE OUTPUTS
            dbc.Row([
                dbc.Col(
                    html.Div([
                        dcc.Graph(id='04_output_fig_co2_dev',
                                  config=config['dash_information']['general']['fig_config']),
                    ]),
                    width=5
                ),

                dbc.Col(
                    html.Div([
                        dcc.Checklist(id='04_input_chkl_countries',
                                      options=[{'label': country, 'value': country}
                                               for country in df_co2_data['country'].unique()],
                                      style={'height': '350px', 'border': '2px solid #000000', 'overflowY': 'scroll',
                                             'opacity': 1, 'transition': 'opacity 0.5s'})
                    ]),
                    width=2
                ),

                dbc.Col(
                    html.Div([
                        dcc.Graph(id='04_output_fig_co2_cmp',
                                  config=config['dash_information']['general']['fig_config'])
                    ]),
                    width=5
                ),
            ]),


        ], id='04_global_co2_consumption'),

        # --------------------------------------------------------------------------------------------------------------
        # 05 DATA & INFORMATION
        dbc.Row([
            # 05.1 DATA & INFORMATION TABLES
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.Div(style={'background-color': default_color, 'height': default_height}),
                        html.H5('Data Sources', style={'paddingTop': default_height}),
                        html.Hr(),
                        dash_table.DataTable(
                            id='data_sources',
                            columns=[
                                {'name': 'Data', 'id': 'data', 'presentation': 'markdown'},
                                {'name': 'Occurrences', 'id': 'occurrences', 'presentation': 'markdown'},
                                {'name': 'Homepage', 'id': 'link_homepage', 'presentation': 'markdown'},
                                {'name': 'Direkt data link', 'id': 'link_data', 'presentation': 'markdown'},
                            ],
                            data=config['data_sources'],
                            style_cell=default_table_style,
                        ),
                        html.Hr(),
                        html.H5('Main used data columns'),
                        html.Hr(),
                        dash_table.DataTable(
                            id='data_columns_information',
                            columns=[
                                {'name': 'Data column', 'id': 'data_column'},
                                {'name': 'Data source', 'id': 'data_source_column'},
                                {'name': 'Description', 'id': 'data_description'},
                            ],
                            data=data_columns_information,
                            style_cell=default_table_style,
                        ),
                        html.Hr(),
                        html.H5('Further information'),
                        html.Hr(),
                        dash_table.DataTable(
                            id='further_information',
                            columns=[
                                {'name': 'Organization', 'id': 'organization', 'presentation': 'markdown'},
                                {'name': 'Homepage', 'id': 'link', 'presentation': 'markdown'},
                            ],
                            data=config['further_information'],
                            style_cell=default_table_style,
                        ),
                        html.Hr(),
                        html.Div(children='© Christopher Wegner, 2023',
                                 style={'background-color': default_color, 'height': default_height,
                                        'text-align': 'right', 'color': 'white', 'paddingRight': 10}),
                    ]),
                    width=12,
                    style={'align-self': 'end'}
                ),
            ], style={'height': '140vh'}),
        ], id='05_data_and_information'),
        ]),
    fluid=True)


app.layout = html.Div([
    html.Script('''
        function scrollToId(id) {
            var element = document.getElementById(id);
            var rect = element.getBoundingClientRect();
            var offset = rect.top - 500;  // Hier definieren wir den Offset von 120 Pixeln
            window.scrollBy({ top: offset, behavior: 'smooth' });
        }
    '''),
    app.layout
])


# ----------------------------------------------------------------------------------------------------------------------
# PRELIMINARY INFORMATION
@app.callback(
    Output('preliminary_information', 'style'),
    Output('hide_button', 'n_clicks'),
    Input('hide_button', 'n_clicks'),
    State('checkbox_show_again', 'value'),
)
def show_preliminary_info(n_clicks, checkbox_value):
    global config

    preliminary_information = config['show_preliminary_info']

    if not preliminary_information:
        return {'display': 'none'}, 0

    # Wenn der Button geklickt wurde und die Checkbox nicht ausgewählt ist, zeige die Informationen nach 1 Sekunde an
    elif n_clicks > 0 and checkbox_value is None:
        return {'display': 'none'}, 0

    # Wenn der Button geklickt wurde und die Checkbox ausgewählt ist, setze die Variable auf False
    elif n_clicks > 0 and 'disable' in checkbox_value:
        config['show_preliminary_info'] = False
        update_config_file(config)
        return {'display': 'none'}, 0


# ----------------------------------------------------------------------------------------------------------------------
# 00 CALLBACK FUNCTION: LOCATION / COORDINATES EXTRACTION FROM INPUT
@app.callback(
    Output('00_output_txt_reference_headline', 'children'),
    Output('00_output_txt_reference_coordinates', 'children'),
    Output('00_output_txt_reference_location', 'children'),
    Output('00_input_btn_reference_coordinates', 'n_clicks'),
    Output('00_input_txt_coordinates', 'value'),
    Output('00_input_txt_coordinates', 'style'),
    Output('00_input_btn_reference_location', 'n_clicks'),
    Output('00_input_txt_location', 'value'),
    Output('00_input_txt_location', 'style'),
    [Input('00_input_btn_reference_coordinates', 'n_clicks')],
    [State('00_input_txt_coordinates', 'value')],
    [Input('00_input_btn_reference_location', 'n_clicks')],
    [State('00_input_txt_location', 'value')]
)
def localize_reference(coordinates_click, coordinates, location_click, location):
    """
    Function for determining the geo-coordinates (if city and state are entered)
    or the location (if coordinates are entered).
    In case of errors appropriate return and no change of output.
    In other cases an appropriate header, location and coordinates of the reference will be displayed.

    :param coordinates_click: Counter of the clicks of the button
    :param coordinates: Coordinates entered
    :param location_click: Counter of the clicks of the button
    :param location: City, State entered
    :return: Reference header, coordinates and location,
                reset of button clicks, input and style of coordinates input,
                reset of button clicks, input and style of location input
    """
    # in case the coordinates button is clicked
    if coordinates_click > 0:
        location, status, message = find_location(coordinates)

        style_input_txt_coordinates = config['dash_information']['00_style_input_txt'][status]
        text_input_txt_coordinates = message

        # if a location could be determined
        if location:
            # change headline
            headline = content['00_navigation_and_reference']['reference_headline']

            return headline, coordinates, location, \
                0, text_input_txt_coordinates, style_input_txt_coordinates,\
                no_update, no_update, no_update

        # if no location could be determined
        else:
            return no_update, no_update, no_update, \
                0, text_input_txt_coordinates, style_input_txt_coordinates, \
                no_update, no_update, no_update

    # in case the location button is clicked
    elif location_click > 0:
        coordinates, status, message = find_coordinates(location)

        style_input_txt_location = config['dash_information']['00_style_input_txt'][status]
        text_input_txt_location = message

        # if coordinates could be determined
        if coordinates:
            # change headline
            headline = content['00_navigation_and_reference']['reference_headline']

            # re-composition of coordinates
            coordinates = f"{round(coordinates.latitude, 7)}, {round(coordinates.longitude, 7)}"

            # relocate with coordinates for uniform city and country display in English
            location, _, _ = find_location(coordinates)

            return headline, coordinates, location, \
                no_update, no_update, no_update, \
                0, text_input_txt_location, style_input_txt_location

        # if no coordinates could be determined
        else:
            return no_update, no_update, no_update, \
                no_update, no_update, no_update, \
                0, text_input_txt_location, style_input_txt_location

    else:
        return no_update, '', '', \
            no_update, no_update, no_update, \
            no_update, no_update, no_update


# ----------------------------------------------------------------------------------------------------------------------
# 01 CALLBACK FUNCTION: WORLD HEATMAP WITH REFERENCE OUTPUT AND COUNTRY HIGHLIGHTING
@app.callback(
    Output('01_output_fig_global_heatmap_temp_anomalies', 'figure'),
    Output('01_output_txt_reference_temp_anomaly', 'children'),
    Output('01_output_txt_figdata_temp_anomaly', 'children'),
    [Input('00_output_txt_reference_coordinates', 'children')],
    [State('00_output_txt_reference_location', 'children')],
    [Input('01_output_fig_global_heatmap_temp_anomalies', 'clickData')],
    [State('01_output_fig_global_heatmap_temp_anomalies', 'figure')],
)
def global_anomalies(coordinates, location, fig_data, current_fig):
    """
    Function for input-independent display of the world heatmap based
    on the latest coordinate-related temperature anomalies.
    If a reference has been entered, the temperature anomaly of the nearest geo-coordinates is displayed.

    :param coordinates: coordinates, if given
    :param location: location, if given
    :param fig_data: data from figure
    :param current_fig: -/-
    :return: figure of world-heatmap,
                temperature anomaly of reference coordinates if given, style (visible / not visible) of text output
    """

    # only latest values
    df = df_anomaly_heatmap[df_anomaly_heatmap['Period'] == df_anomaly_heatmap['Period'].max()]

    # visualization of temperature anomalies on a world map
    fig = px.scatter_geo(df, title=None, hover_data={'Latitude': False, 'Longitude': False, 'Anomaly': ':.2f'},
                         labels={'Anomaly': 'Temperature Anomaly in °C'}, lat='Latitude', lon='Longitude',
                         color='Anomaly', color_continuous_scale="RdYlBu_r", color_continuous_midpoint=0,
                         projection="natural earth", template='plotly', opacity=0.25)

    # hide legend
    fig.update_layout(coloraxis_showscale=False)

    # if coordinates are given
    if coordinates:
        # extract latitude and longitude (rounded & odd values to fit dataset prerequisites)
        latitude, longitude = extract_lat_lon(coordinates)

        # add a marker to the world map at the reference coordinates
        add_marker(fig, latitude, longitude)

        # highlight reference country on worldmap
        countryname_changes = config['dash_information']['01_countryname_changes']
        add_country_shape(fig, gdf_countries, location, countryname_changes)

        # 1. Part output: Textual intro
        text_output_intro = content['01_global_temperature_anomalies']['reference_temp_anomaly_default'].split(':')[0]
        # 2. Part output: extract temperature anomaly value from the dataset
        anomaly_value = df[(df['Latitude'] == latitude) & (df['Longitude'] == longitude)]['Anomaly'].values[-1]

        # composition of the additional outputs (value and visibility)
        text_output_txt_reference = f'{text_output_intro} @ {location} ({coordinates}): {round(anomaly_value, 2)}°C'

    else:
        text_output_txt_reference = no_update

    if fig_data:
        # read latitude and longitude from figdata and combine to coordinates
        latitude = fig_data['points'][0]['lat']
        longitude = fig_data['points'][0]['lon']
        coordinates = f'{latitude}, {longitude}'

        # add a marker to the world map at the reference coordinates
        add_marker(fig, latitude, longitude)

        # find a location if possible (no status or message needed)
        location, _, _ = find_location(coordinates)

        if location:
            # highlight clicked country (if found) on worldmap
            countryname_changes = config['dash_information']['01_countryname_changes']
            add_country_shape(fig, gdf_countries, location, countryname_changes)
        else:
            # otherwise
            location = '[no location available]'

        # 1. Part output: Textual intro
        text_output_intro = content['01_global_temperature_anomalies']['figdata_temp_anomaly_default'].split(':')[0]

        # 2. Part output: extract temperature anomaly value from figure
        anomaly_value = round(fig_data['points'][0]['marker.color'], 2)

        # composition of the additional outputs (value and visibility)
        text_output_txt_fig_data = f'{text_output_intro} @ {location} ({coordinates}): {round(anomaly_value, 2)}°C'
    else:
        text_output_txt_fig_data = no_update

    fig.data = fig.data[::-1]

    return fig, text_output_txt_reference, text_output_txt_fig_data


# ----------------------------------------------------------------------------------------------------------------------
# 02 CALLBACK FUNCTIONS
@app.callback(
    Output('02_output_fig_minmax_temp_anomaly', 'figure'),
    Output('02_output_fig_mean_temp_anomalies', 'figure'),
    [Input('02_input_sld_years', 'value')],
    [Input('00_output_txt_reference_coordinates', 'children')]
)
def local_anomalies(selected_year, coordinates):
    """
    Function for displaying the location-independent extreme values of the temperature anomalies as well as
    the global average values corresponding to the given year.
    If a reference has been entered, the reference is inserted as comparison

    :param selected_year: given year based on dash slider
    :param coordinates: coordinates, if given
    :return: polar line figure of extreme values, line figure of mean values
    """

    # only values of selected year
    df_polar = df_anomaly_heatmap[df_anomaly_heatmap['Year'] == selected_year]

    df_line = df_anomaly_heatmap[['Anomaly', 'Year']].groupby('Year').mean().reset_index()
    df_line['Type'] = 'global mean values'

    # create seperate dataframes for min, max and mean values per month and combine those to one single dataframe
    df_polar_min, df_polar_max, df_polar_mean = extract_min_max_mean_anomalies(df_polar)
    df_polar_min_max_mean = pd.concat([df_polar_max, df_polar_min, df_polar_mean])

    # if coordinates are given
    if coordinates:
        # extract latitude and longitude (rounded & odd values to fit dataset prerequisites)
        latitude, longitude = extract_lat_lon(coordinates)

        # extract specific values for given coordinates
        df_polar_coordinates = df_polar[(df_polar['Latitude'] == latitude) &
                                        (df_polar['Longitude'] == longitude)][['Month', 'Anomaly']]

        # add type of values for comparison
        df_polar_coordinates['Type'] = 'reference values'
        # add values to dataframe
        df_polar_min_max_mean = pd.concat([df_polar_min_max_mean, df_polar_coordinates])

        # extract specific values for given coordinates
        df_line_coordinates = df_anomaly_heatmap[(df_anomaly_heatmap['Latitude'] == latitude) &
                                                 (df_anomaly_heatmap['Longitude'] == longitude)]

        df_line_coordinates = df_line_coordinates[['Anomaly', 'Year']].groupby('Year').mean().reset_index()
        df_line_coordinates['Type'] = 'reference values'

        # add values to dataframe
        df_line = pd.concat([df_line, df_line_coordinates])

    # determination of absolute min, max, min mean and max mean values for uniform display of figures
    abs_min_value = df_anomaly_heatmap['Anomaly'].min()
    abs_max_value = df_anomaly_heatmap['Anomaly'].max()
    abs_min_mean_value = df_line['Anomaly'].min()
    abs_max_mean_value = df_line['Anomaly'].max()

    # convert month numbers to string
    month_dict = config['data_information']['month_number']
    months = list(month_dict.values())
    df_polar_min_max_mean['Month'] = df_polar_min_max_mean['Month'].map(month_dict)

    # creating figures
    fig_polar_line = create_polar_line_figure(df_polar_min_max_mean, abs_min_value, abs_max_value, months)
    fig_line = create_line_figure(df_line, abs_min_mean_value, abs_max_mean_value)

    return fig_polar_line, fig_line


# ----------------------------------------------------------------------------------------------------------------------
# 03 CALLBACK FUNCTION: GLOBAL TEMPERATURE IMPACT
@app.callback(
    Output('03_output_fig_temp_change_co2', 'figure'),
    Output('03_output_fig_temp_change_co2_ranking', 'figure'),
    # Output('03_output_txt_temp_change_co2_description', 'children'),
    Output('03_input_ddl_treemap_grouping_options', 'style'),
    [Input('03_input_tab_worldmap_treemap', 'value')],
    [Input('03_input_ddl_treemap_grouping_options', 'value')],
    [Input('00_output_txt_reference_location', 'children')]
)
def global_temperature_impact(map_type, treemap_option, location):
    """
    Function to show the impact on temperature anomalies due to CO2 emissions by country / grouping.
    Displayed either as a world map with country information only or as a treemap with additional grouping options.
    Additional ranking of the largest polluters and, if given, the reference country.

    :param map_type: type of map (string: world / treemap) to be displayed
    :param treemap_option: grouping options (string) for treemap visualization
    :param location: location, if given
    :return: choropleth / treemap figure of co2-impact on temperature anomalies, bar figure for ranking top polluters,
                description of displayed column, style (visible / not visible) of treemap grouping dropdown list
    """
    # read needed columns
    columns = config['dash_information']['03_df_co2_columns']

    # only needed columns
    df = df_co2_data[df_co2_data['year'] == df_co2_data['year'].max()][columns]

    df = df[df['temperature_change_from_co2'] != 0]

    # determination of absolute min and max values for uniform display of figures
    abs_min_value = df['temperature_change_from_co2'].min()
    abs_max_value = df['temperature_change_from_co2'].max()

    # label-creation
    labels = {'temperature_change_from_co2':
                  df_co2_codebook.loc['temperature_change_from_co2', 'description'].split('.')[0],
              'co2':
                  df_co2_codebook.loc['co2', 'description'].split('.')[0]}

    # if tab is on worldmap (default)
    if map_type == 'world':
        # create choropleth figure
        fig = px.choropleth(df, title=None, locations='iso_code',
                            hover_name='country',
                            hover_data={'temperature_change_from_co2': ':.5f', 'iso_code': False, 'co2': ':.2f'},
                            color='temperature_change_from_co2', color_continuous_scale='Reds',
                            labels=labels,
                            projection='natural earth', template='plotly')

        # hide legend
        fig.update_layout(coloraxis_showscale=False)

        # hide dropdown list (only for treemap visualization)
        style_input_ddl_treemap = config['dash_information']['03_style_input_ddl_treemap']['not_visible']

    # if tab is on treemap
    else:
        # show dropdown list (only for treemap visualization)
        style_input_ddl_treemap = config['dash_information']['03_style_input_ddl_treemap']['visible']

        if treemap_option.split('#')[0] == 'all':
            parent_column = treemap_option.split('#')[1]
            df_treemap = df.dropna(subset=parent_column)

            fig = px.treemap(df_treemap, path=[parent_column, 'country'], values='temperature_change_from_co2',
                             color='temperature_change_from_co2', color_continuous_scale='Reds',
                             range_color=[abs_min_value, abs_max_value], hover_name='country')

        else:
            parent_value = treemap_option.split('#')[0]
            parent_column = treemap_option.split('#')[1]
            df_treemap = df[df[parent_column] == parent_value]

            fig = px.treemap(df_treemap, path=['country'], values='temperature_change_from_co2',
                             color='temperature_change_from_co2', color_continuous_scale='Reds',
                             range_color=[abs_min_value, abs_max_value], hover_name='country')

        # update for change in hover template
        fig.update_traces(hovertemplate='<b>%{label}</b><br><br>Temperature change in °C: %{value}')
        fig.update_layout(coloraxis_showscale=False)

    # sort by column 'temperature_change_from_co2' for display order and filtering main polluters
    df = df.sort_values('temperature_change_from_co2', ascending=True)

    # filter data records with the 20 highest entries
    df_top20 = df.tail(20)

    # if a location is given
    if location != '':
        # only country
        location = location.split(', ')[1]

        # check if reference location is already in top 20 (TRUE/FALSE)
        location_present = df_top20['country'].str.contains(location).any()

        # if reference location is not yet included
        if not location_present:
            # filter and add data for reference location
            df_location = df[df['country'] == location]
            df_top20 = pd.concat([df_top20, df_location]).sort_values('temperature_change_from_co2', ascending=True)

    # # create bar figure (ranking)
    fig_ranking = px.bar(df_top20, orientation='h', x='temperature_change_from_co2', y='country',
                         hover_data={'temperature_change_from_co2': ':.5f', 'country': False},
                         labels={'temperature_change_from_co2': 'Temperature change in °C'},
                         color='temperature_change_from_co2', color_continuous_scale='Reds',
                         range_color=[abs_min_value, abs_max_value])

    # hide titles of axes and define auxiliary lines
    fig_ranking.update_yaxes(title_text='')
    fig_ranking.update_xaxes(title_text='', gridcolor='black', tickvals=[i/10 for i in range(int(abs_max_value*10)+1)])

    # change background-color, hide legend and highlight (=bold) reference location on y-axis (if given)
    y_values = fig_ranking.data[0]['y']
    fig_ranking.update_layout(coloraxis_showscale=False, plot_bgcolor='white',
                              yaxis=dict(
                                  tickvals=y_values,
                                  ticktext=[country
                                            if country != location
                                            else f'<b>{country}</b>' for country in y_values])
                              )

    # read data description of displayed column from codebook
    # column_description = df_co2_codebook.loc['temperature_change_from_co2', 'description']

    return fig, fig_ranking, style_input_ddl_treemap


# ----------------------------------------------------------------------------------------------------------------------
# 04 CALLBACK FUNCTIONS
@app.callback(
    Output('04_output_fig_co2_dev', 'figure'),
    Output('04_output_fig_co2_cmp', 'figure'),
    # Output('04_output_txt_co2_dev_description', 'children'),
    Output('04_input_chkl_countries', 'style'),
    [Input('04_input_ddl_grouping_options', 'value')],
    [Input('04_input_rsl_years', 'value')],
    [Input('04_input_chkl_countries', 'value')],
    [Input('00_output_txt_reference_location', 'children')]
)
def co2_development(grouping_option, xy_years, countries, location):
    """
    Function to show the development of co2 consumption of individual countries or groups of countries.
    Presentation of consumption over the entire period on the one hand,
    and direct comparison between two selected years on the other.
    If given, the reference country is added to the figures.

    :param grouping_option: hash-separated string for grouping control
    :param xy_years: List of years to be compared
    :param countries: List of countries - if no grouping (according to grouping_option)
    :param location: location, if given
    :return: line figure for co2-consumption over years, scatter figure for comparison of co2-consumption,
                description of displayed column, style (visible / not visible) of country checklist
    """
    # group / filter original dataframe depending on input (grouping_option)
    if grouping_option is None:
        return no_update, no_update, no_update

    elif grouping_option.split('#')[0] == 'grouping':
        # extract the column to group by
        group = grouping_option.split('#')[1]

        # read default columns to be used
        columns_grouping = set(config['dash_information']['04_df_co2_columns_grouping'])

        # group base dataframe
        df_development = group_df(df_co2_data, columns_grouping, group, location)

        # define base of color for figures
        color_figures = group

        # update style depending on input (country checklist / no country checklist)
        style_input_chkl_countries = config['dash_information']['04_style_input_chkl_countries']['not_visible']

    elif grouping_option.split('#')[0] == 'filter':
        # extract the column to filter by
        filter_column = grouping_option.split('#')[1]

        # extract the value to filter for
        filter_value = grouping_option.split('#')[2]

        # read default columns to be used
        columns_filter = set(config['dash_information']['04_df_co2_columns_filter'])

        # filter base dataframe
        df_development = filter_df(df_co2_data, columns_filter, filter_column, filter_value, location)

        # define base of color for figures
        color_figures = 'country'

        # update style depending on input (country checklist / no country checklist)
        style_input_chkl_countries = config['dash_information']['04_style_input_chkl_countries']['not_visible']

    else:
        # update style depending on input (country checklist / no country checklist)
        style_input_chkl_countries = config['dash_information']['04_style_input_chkl_countries']['visible']

        if not countries:
            return no_update, no_update, style_input_chkl_countries
        else:
            # determine the column to filter by
            filter_column = 'country'

            # transfer the values (countries) to filter for
            filter_value = countries

            # read default columns to be used
            columns = config['dash_information']['04_df_co2_columns_filter']

            # group base dataframe
            df_development = filter_df(df_co2_data, columns, filter_column, filter_value, location)

            # define base of color for figures
            color_figures = 'country'

    # division of the range slider into separate variables
    x_year = xy_years[0]
    y_year = xy_years[1]

    # create dataframe for comparison based on the years to be compared
    df_comparison = xy_filter_df(df_development, color_figures, x_year, y_year)

    # create figures
    fig_development = create_co2_consumption_fig(df_development, color_figures, x_year, y_year)
    fig_comparison = create_co2_comparison_fig(df_comparison, color_figures, x_year, y_year)

    # highlight (=bold) reference location in legend (if given)
    if location != '':
        for i, d in enumerate(fig_development.data):
            if d.name == location:
                fig_development.data[i].name = '<b>' + d.name + '</b>'

        for i, d in enumerate(fig_comparison.data):
            if d.name == location:
                fig_comparison.data[i].name = '<b>' + d.name + '</b>'

    # read data description of displayed column from codebook
    column_description = df_co2_codebook.loc['consumption_co2', 'description'], \
        df_co2_codebook.loc['consumption_co2_per_capita', 'description']

    return fig_development, fig_comparison, style_input_chkl_countries


app.run_server(port=8051, debug=True)
# app.run_server(port=8051)
