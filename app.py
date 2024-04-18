import plotly.graph_objects as go
from dash_bootstrap_templates import load_figure_template
import pandas as pd
import os
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table
import dash
import dash_bootstrap_components as dbc


os.chdir("/Users/annaolsen/Desktop/Speciale/DS_thesis/data")
print(os.getcwd())

# ------- Load and prepare datasets -------
df = pd.read_csv("Tara_BMN_Cleaned.csv")

# Removing rows with empty longitude or latitude
df = df.dropna(subset=['Latitude', 'Longitude'])

# Reset the index after dropping rows
df.reset_index(drop=True, inplace=True)

# df_sst = pd.read_csv("Tara_SST_Plot.csv")
# df = df[:1000]

all_data_points = len(df)

h6_style = {'fontWeight': "bold", 'marginTop': 20, 'marginBottom': 10}

df = df.assign(**{"no_col": "Sample point"})

df_time = df.copy()

df = df.sort_values(by=['Date'])


# Function to find numeric columns


def numeric_columns(df):
    numeric_cols = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
    return numeric_cols


numeric_cols = numeric_columns(df)
# print(numeric_cols)

# Fill missing values in the entire DataFrame
df.fillna('NaN', inplace=True)


# ------- Year slider -------
year_min, year_max = df['Year'].min(), df['Year'].max()

all_years = list(range(year_min, year_max + 1))  # Find all years within range

year_marks = {year: str(year)
              for year in all_years}  # Create marks for each year


# ------- Dropdown - Explore missing values -------

dropdown_options = [{'label': col, 'value': col} for col in df.columns[1:]]

# Dropdown - time series
dropdown_time_options = [{'label': col, 'value': col}
                         for col in numeric_cols if col != 'Date']


# ---------- Data for scatter plot and dropdown menus ----------
cols_x = ['Sea Surface Temp', 'Depth top',
          'Depth nominal', 'Depth layer zone',
          'Nitrate', 'Chlorophyll a',
          'Phosphate median', 'Phosphate max' 'Net PP carbon']

# Options for dropdown menu (x-axis)
scatter_options_x = [{'label': col, 'value': col} for col in cols_x]

cols_y = ['Shannon_Darwin_mean_all', 'SILVA_Chao', 'SILVA_ace',
          'SILVA_species_rich', 'SILVA_func_diversity', 'Sea Surface Temp',
          'Depth top', 'Depth nominal', 'Nitrate', 'Chlorophyll a']

# Options for dropdown menu (y-axis)
scatter_options_y = [{'label': col, 'value': col} for col in cols_y]


# ------- Left sidebar for filtering -------
SIDEBAR_STYLE = {
    "marginTop": 15,
    "top": 0,
    "left": 0,
    "bottom": 0,
    "paddingLeft": '20px',
    "paddingRight": '10px',
    "paddingTop": "28px",
    "paddingBottom": '10px',
    "background-color": "#f8f9fa",
}

sidebar = html.Div([
    html.H4("Filters"),
    html.Hr(),
    html.H6('Color points by category:', style=h6_style),
    dbc.RadioItems(
        options=[
            {"label": 'No colors', "value": 'no_col'},
            {"label": 'Marine biome', "value": 'MP biome'},
            {"label": 'Ocean and sea region', "value": 'OS region'},
            {"label": 'Depth layer zone', "value": 'Depth layer zone'},
            {"label": 'Biogeographical province', "value": 'BG province'},
            {"label": 'Campaign', "value": 'Campaign'},
        ],
        value="no_col",
        id="map-color-input",
        style={'marginTop': 10, 'marginBottom': 25},
    ),
    html.H6('Years',
            style={'fontWeight': "bold", 'marginTop': 15, 'marginBottom': 15}),
    dcc.RangeSlider(
        id='year_range_slider',
        min=year_min,
        max=year_max,
        step=1,
        marks=year_marks,
        value=[year_min, year_max],
    ),
    html.H6("Explore missing values",
            style={'fontWeight': "bold", 'marginTop': 25, 'marginBottom': 12}),
    dcc.Dropdown(
        id='value_dropdown',
        options=dropdown_options,
        value=df.columns[1],  # Default value
        clearable=False
    ),
    dbc.RadioItems(
        id='checklist',
        options=[
            {'label': 'All points', 'value': 'all'},
            {'label': 'Values', 'value': 'values'}
        ],
        value='all',
        inline=True,
        style={'marginTop': 10, 'marginBottom': 10},
    ),
    html.Div([
        html.P("Filtered data:",
               style={'marginBottom': 0, 'marginLeft': 0,
                      'marginTop': 25, 'font-size': '16px'}),
        html.Div(id='filtered-count', style={
            'marginBottom': 0, 'font-size': '16px',
            'marginTop': 25,
            'font-weight': 'bold', 'marginLeft': 30}),
    ], style={'display': 'flex'}),
    html.Div([
        html.P("All data:",
               style={'textAlign': 'left',
                      'marginBottom': 20, 'marginLeft': 0,
                      'font-size': '16px'}),
        html.P(f"{all_data_points}",
               style={'textAlign': 'left',
                      'fontWeight': "bold",
                      'marginBottom': 0,
                      'marginLeft': 65,
                      'font-size': '16px'})
    ], style={'display': 'flex'}),
],
    style=SIDEBAR_STYLE)


# ------- Info box -------

# Define the style for the card containing the info
info_box_style = {'margin-top': '15px', 'marginBottom': '15px',
                  'padding': '15px', 'background-color': '#f0f0f0',
                  'line-height': '1.1'}

info_box_style_a = {'margin-top': '15px', 'marginBottom': '15px',
                    'marginLeft': '0px',
                    'padding': '0px', 'background-color': '#f0f0f0',
                    'line-height': '1.1'}

# Define the layout for the info box
info_box = dbc.Card([
    dbc.CardBody([
        html.H5("Explore points", className="card-title",
                style={'marginBottom': '10px'},
                id='selected_point_info_header'),
        html.P("Click on a point to display its information.",
               className="card-text", id='selected_point_info_text')
    ])
], style=info_box_style)


box_options = [
    {'label': 'Sea Surface Temp', 'value': 'Sea Surface Temp'},
    {'label': 'Nitrate', 'value': 'Nitrate'},
    {'label': 'Phosphate', 'value': 'Phosphate median'},
    {'label': 'Depth top', 'value': 'Depth top'},
    {'label': 'Depth nominal', 'value': 'Depth nominal'},
    {'label': 'Chlorophyll a', 'value': 'Chlorophyll a'},
]


# ------- Plotly, dash and mapbox -------
px.set_mapbox_access_token(
    'pk.eyJ1Ijoia29ydHBsb3RseSIsImEiOiJjbHBoNDZmZm0wMHUyMnJwNm5yM3RtcjY1In0.qxuHfESjhBp1wqT9ByZc0g')


# create the dash application using the above layout definition
app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# load_figure_template('FLATLY')
# Makes the Bootstrap Themed Plotly templates available
load_figure_template("cerulean")


# -------------------- Dashboard layout --------------------
app.layout = html.Div([
    dbc.Container([
        dbc.Row([  # Row with sidebar, ocean map, info box
            dbc.Col(
                sidebar, width=2),  # Sidebar
            dbc.Col([
                html.Div([
                    html.H3(children='TARA Oceans')],
                    style={'textAlign': 'center', 'marginTop': 20,
                           'marginBottom': 10}),
                html.Div([  # Ocean map
                    dcc.Graph(id='ocean_map',
                              clickData={'points': [{'customdata': ''}]}
                              ),
                    dcc.Input(id='dummy-input', type='hidden',
                              value='trigger-callback'),
                ])], width=7, className="scatter_map"),
            dbc.Col(  # Info box
                html.Div([
                    html.Div(id='selected_point_info_box'),
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Attribute for box plot"),
                            dcc.Dropdown(
                                id='boxplot_dropdown',
                                options=box_options,
                                value='Sea Surface Temp',  # Default value
                                clearable=False,
                                style={'width': '90%', 'marginBottom': '10px',
                                       'marginTop': '10px'}),
                            dcc.Graph(id='box_plot', figure={}),
                            # Add a hidden div to store the selected point information
                            html.Div(id='selected_point_info',
                                     style={'display': 'none'}),
                        ])
                    ], style=info_box_style)
                ]),
                width=3),
        ]),
        dbc.Row([
            html.Div([
                html.P('', style={'marginBottom': 10, 'marginTop': 15})
            ])
        ]),
        dbc.Row([dbc.Col([
                dcc.Dropdown(
                    id='dropdown_time',
                    options=dropdown_time_options,
                    value='Sea Surface Temp',  # Default value
                    clearable=False
                ),
                dcc.Graph(id='timeseries')]),]),
        dbc.Row([  # Row with scatter plot and bar chart
            # dbc.Col(
            #     html.Div([  # Dropdown for scatter plot
            #         html.P('Attribute for x-axis:',
            #                style={'fontWeight': "bold",
            #                       'marginTop': 30,
            #                       'marginBottom': 5,
            #                       'font-size': 16}),
            #         dcc.Dropdown(id='scatter_dropdown_x',
            #                      options=scatter_options_x,
            #                      multi=False,
            #                      clearable=False,
            #                      value='Sea Surface Temp',
            #                      style={'marginTop': 0}),
            #         html.P('Attribute for y-axis:',
            #                style={'fontWeight': "bold",
            #                       'marginTop': 30,
            #                       'marginBottom': 5,
            #                       'font-size': 16}),
            #         dcc.Dropdown(id='scatter_dropdown_y',
            #                      options=scatter_options_y,
            #                      multi=False,
            #                      clearable=False,
            #                      value='SILVA_species_rich',
            #                      style={'marginTop': 0}),
            #         html.P('Color by attribute:',
            #                style={'fontWeight': "bold",
            #                       'marginTop': 30,
            #                       'marginBottom': 5,
            #                       'font-size': 16}),
            #         dcc.Dropdown(id='scatter_color',
            #                      options=[
            #                         {'label': 'Sea Surface Temp',
            #                             'value': 'Sea Surface Temp'},
            #                         {'label': 'Latitude', 'value': 'Latitude'},
            #                         {'label': 'Depth', 'value': 'Depth top'},
            #                      ],
            #                      multi=False,
            #                      clearable=False,
            #                      value='Latitude',
            #                      style={'marginTop': 0}),

            #     ]), width=2),
            # dbc.Col(
            #     html.Div([  # Scatter plot
            #         dcc.Graph(id='scatter_plot')]),
            #     width=7, className="scatter_plot"),
            # dbc.Col(
            #     html.Div([  # Bar chart
            #         dcc.Graph(id='sample_count_bar'),
            #     ]), width=4, className="sample_count_bar"),
        ]),

    ], fluid=True),
])


# ------- Box plot (selected point) -------

@app.callback(
    Output('box_plot', 'figure'),
    [Input('selected_point_info', 'children'),
     Input('boxplot_dropdown', 'value'),
     Input('map-color-input', 'value')]
)
def update_box_plot(selected_point_info, selected_column, color_category):

    # fig = px.box(df, y=selected_column, title=f'Box Plot of {selected_column}')

    fig = go.Figure(
        data=[go.Box(y=df[selected_column],
                     boxpoints=False,  # 'all', 'outliers', or 'suspectedoutliers'
                     jitter=0.7,  # add some jitter for a better separation between points
                     pointpos=-1.8,  # relative position of points wrt box
                     name="All",  # Set the name for the first box plot
                     showlegend=False,
                     hoverinfo='y',
                     )])

    # If a point is selected, add a marker for the selected point on the box plot
    if selected_point_info and 'lat' in selected_point_info and 'lon' in selected_point_info:
        lat = selected_point_info['lat']
        lon = selected_point_info['lon']
        selected_row = df[(df['Latitude'] == lat) &
                          (df['Longitude'] == lon)]

        if not selected_row.empty:
            selected_row = selected_row.iloc[0]
            selected_value = selected_row[selected_column]

            if selected_value != "NaN":
                # If selected value is not NaN, show legend as "point"
                legend_name = 'Point'
                marker_style = dict(color='red', size=10)
            else:
                # If selected value is NaN, show legend as "NaN"
                legend_name = 'NaN'
                marker_style = dict(color='black', size=10)

            fig.add_trace(go.Scatter(
                x=["All"], y=[selected_value], mode='markers',
                marker=marker_style, name=legend_name, hoverinfo='y',
                showlegend=True))

            # If a color category is selected, add a box plot only for the selected subcategory
            if color_category:
                selected_category = selected_row[color_category]
                category_data = df[df[color_category] ==
                                   selected_category][selected_column]
                fig.add_trace(go.Box(
                    y=category_data,
                    boxpoints=False,
                    jitter=0.7,
                    pointpos=-1.8,
                    name=f"{selected_category}",
                    showlegend=False,
                    hoverinfo='y'
                ))

                # Add red marker for selected point in the second box plot
                fig.add_trace(go.Scatter(
                    x=[selected_category],
                    y=[selected_value],
                    mode='markers',
                    marker=dict(color='red', size=10),
                    name='Point',
                    hoverinfo='y',
                    showlegend=False
                ))

    # Adjust the margins
    fig.update_layout(
        title=f'{selected_column}',  # Set the title
        title_x=0.5,  # Center the title
        title_y=0.94,
        margin=dict(t=40, l=40, b=20, r=0),  # Margin of plot
        legend=dict(x=0.82, y=1.05),
        height=300,
        width=310,
    )

    return fig


# Callback to store the selected point information when a point is clicked on the map
@app.callback(
    Output('selected_point_info', 'children'),
    [Input('ocean_map', 'clickData')]
)
def store_selected_point_info(clickData):
    if clickData:
        selected_point_info = clickData['points'][0]
        return selected_point_info
    else:
        return None


# ------- Ocean map - Plot sample locations -------

# Define your list of colors
custom_colors = ['#5F676C', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#edbf33',
                 '#8c564b', '#e377c2', '#8be04e', '#1f77b4', '#0bb4ff', '#7f7f7f',  '#bcbd22', '#17becf',
                 '#ff7f0e', '#1f77b4', '#2ca02c', '#d62728', '#9467bd',
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                 '#ff7f0e', '#1f77b4', '#2ca02c', '#d62728', '#9467bd',
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                 '#ff7f0e', '#1f77b4', '#2ca02c', '#d62728', '#9467bd',
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                 '#ff7f0e', '#1f77b4', '#2ca02c', '#d62728', '#9467bd',
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                 '#ff7f0e', '#1f77b4', '#2ca02c', '#d62728', '#9467bd',
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Define the labels dictionary
legend_labels = {
    "no_col": "",
    "MP biome": "Marine biome",
    "OS region": "Ocean and sea region",
    "Depth layer zone": "Depth layer zone",
    "BG province": "Biogeographical province",
    "Campaign": "Campaign",
}


@app.callback(
    [Output('ocean_map', 'figure'),
     Output('filtered-count', 'children')],
    [Input('year_range_slider', 'value'),
     Input('value_dropdown', 'value'),
     Input('checklist', 'value'),
     Input('map-color-input', 'value')])
def plot_samples_map(year_range, selected_column, checklist, color_by):

    dff = df[df['Year'].between(year_range[0], year_range[1])]

    # dff['location'] = list(zip(dff['Latitude'], dff['Longitude']))
    # dff = dff.drop_duplicates(subset=['location'])

    # Filter DataFrame based on selected column and checklist options
    if 'values' in checklist:
        dff = dff[dff[selected_column] != 'NaN']  # Filter out rows with 'NaN'

    fig = px.scatter_mapbox(dff,
                            lat=dff['Latitude'],
                            lon=dff['Longitude'],
                            color=color_by,
                            color_discrete_sequence=custom_colors,
                            zoom=0.8, height=700,
                            title=None, opacity=.5,
                            custom_data=['Sample ID',
                                         'OS region',
                                         'Date', 'MP biome',
                                         'Sea Surface Temp', 'Depth top',
                                         'Depth nominal', 'Depth layer zone',
                                         'Sea ice conc', 'Net PP carbon',
                                         'Station', 'Phosphate median',
                                         'Latitude', 'Longitude'],
                            )

    # Define a custom hover template
    hover_template = '<b>%{customdata[0]}</b><br>' \
        'Station: %{customdata[10]}</b><br>' \
        'Region: %{customdata[1]}<br>' \
        'Date: %{customdata[2]}<br>' \
        'Marine biome: %{customdata[3]}<br>' \
        'Temperature: %{customdata[4]:.2f}<br>' \
        'Depth: %{customdata[5]}<br>' \
        'Depth nominal: %{customdata[6]}<br>' \
        'Phosphate: %{customdata[11]}<br>' \
        '%{customdata[7]}<br>' \
        'Sea Ice Concentration: %{customdata[8]}<br>' \
        'Net primary production of carbon: %{customdata[9]}<br>' \
        'Lat: %{customdata[12]:.3f}, Lon: %{customdata[13]:.3f}<extra></extra>'

    # Update the hover template
    fig.update_traces(hovertemplate=hover_template)

    # # Add points from df2 as a separate scatter plot
    # fig.add_scattermapbox(
    #     lat=df_sst['sst_lat'],
    #     lon=df_sst['sst_lon'],
    #     mode='markers',
    #     # marker=dict(color=df_sst['OS region'],
    #     #             colorscale='Viridis',  # Use the same color scale as the main plot
    #     #             # Add colorbar for temperature
    #     #             colorbar=dict(title='OS region')),
    #     text=df_sst['Sample ID'],  # Display Sample ID as hover text
    #     name='Additional Points',  # Name for the legend
    #     # Custom data for hover
    #     customdata=df_sst[['Sample ID', 'sst_daily', 'Sea Surface Temp',
    #                        'sst_lat', 'sst_lon', 'Latitude', 'Longitude']],
    #     hovertemplate="<b>%{customdata[0]}</b><br>" +
    #     "Temperature (SST): %{customdata[1]:.2f}<br>" +
    #     "Tara SST: %{customdata[2]:.2f}<br>" +
    #     "Lat: %{customdata[3]}, Lon: %{customdata[4]}<br>" +
    #     "(Tara Lat: %{customdata[5]:.3f}, Lon: %{customdata[6]:.3f}<extra></extra>"

    # )

    # Update the legend title dynamically based on the selected option
    # Default to "Legend" if color_by not found

    legend_title = legend_labels.get(color_by, "Legend")
    fig.update_layout(
        mapbox_style='mapbox://styles/kortplotly/clsyukswv002401p8a4xtbbm3',
        margin={"r": 0, "l": 0, "b": 0, "t": 0},
        showlegend=True,
        legend=dict(
            orientation="h",
            x=0,
            yanchor="top",
            y=1.05,
            title=legend_title  # Set the legend title dynamically
        )
    )

    # to preserve the UI settings such as zoom and panning in the update
    fig['layout']['uirevision'] = 'unchanged'

    # Get the count of filtered records
    count = len(dff)

    return [fig, f"{count}"]


# ------- Clicks on map -------

# Define the style for the table
table_style = {
    'margin-top': '0px',
    'margin-bottom': '0px',
    'padding': '3px',
    'background-color': '#f0f0f0',
    'line-height': '1.7',
    'overflowX': 'auto',
    'width': '100%',
}


@app.callback(
    Output('selected_point_info_box', 'children'),
    [Input('ocean_map', 'clickData')]
)
def display_selected_point_info(clickData):
    if clickData is not None:
        selected_point = clickData['points'][0] if clickData['points'] else None
        if selected_point:
            lat = selected_point.get('lat')
            lon = selected_point.get('lon')

            # Find the row in the DataFrame corresponding to the clicked point
            selected_rows = df[(df['Latitude'] == lat) &
                               (df['Longitude'] == lon)]

            if not selected_rows.empty:
                selected_row = selected_rows.iloc[0]

                sample_id = selected_row['Sample ID']
                date = selected_row['Date']
                os_region = selected_row['OS region']
                marine_biome = selected_row['MP biome']

                depth_layer = selected_row['Depth layer zone']
                depth_top = selected_row['Depth top']
                sea_surface_temp = selected_row['Sea Surface Temp']

                nitrate = selected_row['Nitrate']
                phosphate_med = selected_row['Phosphate median']
                phosphate_max = selected_row['Phosphate max']
                chlorophyll = selected_row['Chlorophyll a']
                carbon_production = selected_row['Net PP carbon 30']

                if lat is not None and lon is not None:
                    data = [
                        {"Col": "Sample ID", "Value": sample_id},
                        {"Col": "Date", "Value": date},
                        {"Col": "Region", "Value": os_region},
                        {"Col": "Marine biome", "Value": marine_biome},
                        {"Col": "Depth Layer Zone", "Value": depth_layer},
                        {"Col": "Depth (top)", "Value": depth_top},
                        {"Col": "Sea Surface Temp",
                            "Value": sea_surface_temp},

                        {"Col": "Nitrate (M)", "Value": nitrate},
                        {"Col": "Phosphate (median)", "Value": phosphate_med},
                        {"Col": "Phosphate (max)", "Value": phosphate_max},
                        {"Col": "Chlorophyll", "Value": chlorophyll},
                        {"Col": "Carbon production", "Value": carbon_production},
                    ]

                    # Define the DataTable for selected point information
                    selected_info_table = dash_table.DataTable(
                        columns=[{"name": "Attribute", "id": "Col"},
                                 {"name": "Value", "id": "Value"}],
                        data=data,
                        style_table=table_style,
                        style_data_conditional=[
                            {'if': {'row_index': 'odd'},
                             'backgroundColor': '#f8f9fa',
                             }],
                        style_cell={'fontSize': '13px',
                                    'whiteSpace': 'normal',
                                    'paddingLeft': '10px',
                                    'paddingRight': '10px',
                                    'textAlign': 'left'},

                        style_header={
                            # 'backgroundColor': 'rgb(210, 210, 210)',
                            'color': 'black',
                            'fontWeight': 'bold'
                        },
                        page_size=6,   # Display 8 values per page
                    )

                    return dbc.Card([
                        html.H5("Explore points", className="card-title",
                                style={'marginTop': '15px',
                                       'marginBottom': '0px',
                                       'marginLeft': '15px',
                                       'paddingLeft': '15px',
                                       'paddingTop': '15px'}),
                        dbc.CardBody(selected_info_table)
                    ], style=info_box_style_a)
    # If no point is clicked, display default message
    return info_box


# ------- Scatter plot (updates based on selected attributes) -------
# @app.callback(
#     Output('scatter_plot', 'figure'),
#     [Input('year_range_slider', 'value'),
#      Input('scatter_dropdown_x', 'value'),
#      Input('scatter_dropdown_y', 'value'),
#      Input('scatter_color', 'value')]
# )
# def update_scatter_plot(year_range, attribute_x, attribute_y, color_by):

#     dff = df[df['Year'].between(year_range[0], year_range[1])]

#     plot_columns_x = ['Sea Surface Temp']
#     plot_columns_y = ['SILVA_species_rich']

#     # Add selected attributes to the plot columns if they exist
#     if attribute_x:
#         plot_columns_x[0] = attribute_x

#     if attribute_y:
#         plot_columns_y[0] = attribute_y

#     print(f"Plot Columns x: {plot_columns_x} and y: {plot_columns_y}")

#     # Create scatter plot
#     fig = px.scatter(dff,
#                      height=600,
#                      x=plot_columns_x[0],
#                      y=plot_columns_y[0],
#                      color=color_by,
#                      hover_name='Year',
#                      title='Scatter Plot')

#     return fig


# print(df['OS region'].unique())
# Create a dictionary to map each region to its corresponding color
region_color_mapping = {
    'Mediterranean Sea': 'rgba(255, 0, 0, 0.2)',
    'Red Sea': 'rgba(0, 255, 0, 0.2)',
    'Indian Ocean': 'rgba(0, 0, 255, 0.2)',
    'South Atlantic Ocean': 'rgba(92, 192, 232, 0.2)',
    'Southern Ocean': 'rgba(92, 232, 99, 0.2)',
    'South Pacific Ocean': 'rgba(84, 71, 245, 0.2)',
    'North Pacific Ocean': 'rgba(159, 174, 164, 0.2)',
    'North Atlantic Ocean': 'rgba(245, 236, 71, 0.2)',
    'Arctic Ocean': 'rgba(38, 165, 150, 0.2)',
}


# Add a new column to the DataFrame to store the color for each region
df_time['Region Color'] = df_time['OS region'].map(region_color_mapping)


# ------- Time series plot -------

def reduce_datapoints(df, focus_attribute, percentage_threshold):
    max_val = df[focus_attribute].max()
    min_val = df[focus_attribute].min()
    val_range = max_val - min_val

    percentage_diff = (
        np.abs(df[focus_attribute][1:].to_numpy() -
               df[focus_attribute][0:-1].to_numpy())
        / val_range
    )

    mask_a = percentage_diff < percentage_threshold
    mask_b = df["Date"][1:].to_numpy() == df["Date"][0:-1].to_numpy()
    mask_a = np.insert(mask_a, 0, False, axis=0)
    mask_b = np.insert(mask_b, 0, False, axis=0)

    mask = mask_a * mask_b
    mask_valid = mask == False

    mask_c = df[focus_attribute].isna()
    mask_nan = (mask_b == False) * mask_c

    df_temp = df[0:]
    df_valid = df_temp[mask_valid]
    df_nan = df_temp[mask_nan]
    df_nan[focus_attribute] = min_val - (val_range * 0.05)
    max_value = max_val + (val_range * 0.1)
    min_value = min_val - (val_range * 0.1)
    # df_nan = df_temp[df_temp[focus_attribute].isna()]

    return df_valid, df_nan, max_value, min_value


@app.callback(
    Output('timeseries', 'figure'),
    [Input('dropdown_time', 'value'),
     Input('selected_point_info', 'children'),
     Input('map-color-input', 'value')]
)
def update_timeseries(selected_variable, selected_point_info, color_by):
    fig = go.Figure()
    df_temp = df_time.copy()
    df_temp = df_temp.dropna(subset=["Latitude", "Longitude"])
    df_temp = df_temp.sort_values(by=["Date", selected_variable])
    df_temp.reset_index(drop=True, inplace=True)

    dff, dff_nan, max_value_plot, min_value_plot = reduce_datapoints(
        df_temp, selected_variable, 0.01)

    # Get unique values in the selected category
    unique_values = dff[color_by].unique()

    # Generate a colorscale based on the unique values
    num_unique_values = len(unique_values)
    colorscale = custom_colors[:num_unique_values]

    # Create a mapping dictionary for colors based on the unique values
    category_color_mapping = dict(zip(unique_values, colorscale))

    # Map the colors based on the unique values and create a new 'Color' column
    dff['Color'] = dff[color_by].map(category_color_mapping)

    # Points with values
    fig.add_trace(go.Scatter(
        x=dff['Date'],
        y=dff[selected_variable],
        mode='markers+lines',
        marker=dict(
            # Use the 'Color' column for coloring the points
            color=dff['Color'],
        ),
        line=dict(color='lightgrey'),
        # line=dict(color=dff['Color']),

        name="With value"),
    )
    # fillcolor=color_by,
    # color_discrete_sequence=custom_colors,
    # marker=dict(size=6,
    #             # color='DarkSlateGray',
    #             color=color_by,
    #             color_discrete_sequence=custom_colors,
    #             ),
    #    name = "With value"),
    # )

    # Points with NaN-values
    fig.add_trace(go.Scatter(
        x=dff_nan['Date'],
        y=dff_nan[selected_variable],
        mode='markers', marker=dict(size=6, color='lightgrey'),
        name="Without value"))

    # If a point is selected, add a marker for the selected point on the box plot
    if selected_point_info and isinstance(selected_point_info, dict) and 'lat' in selected_point_info and 'lon' in selected_point_info:
        lat = selected_point_info['lat']
        lon = selected_point_info['lon']
        selected_row = df_temp[(df_temp['Latitude'] == lat) &
                               (df_temp['Longitude'] == lon)]

        if not selected_row.empty:
            selected_row = selected_row.iloc[0]
            selected_value = selected_row[selected_variable]
            selected_date = selected_row['Date']

            fig.add_trace(go.Scatter(
                x=[selected_date], y=[selected_value], mode='markers',
                marker=dict(color='red', size=15, opacity=0.75), name="Point",
                showlegend=True))

    # Adding vertical lines for specific dates
    years_to_mark = [2010, 2011, 2012, 2013]  # Specify the years
    for year in years_to_mark:

        # January 1st of each year
        line_date = pd.Timestamp(year, 1, 1)

        fig.add_shape(type="line",
                      x0=line_date, y0=min_value_plot,
                      x1=line_date, y1=max_value_plot,
                      line=dict(color="black",
                                width=1, dash="dash"),
                      )

        fig.add_annotation(x=line_date, y=max_value_plot,
                           text=str(year), showarrow=False,
                           xshift=30, yshift=-10,
                           font=dict(color="black", size=11)
                           )

    # fig.update_traces(line_color=dff['Color'].iloc[:, 1])

    fig.update_layout(
        title=f'{selected_variable} over time',
        title_x=0.5,  # Center the title
        title_y=0.96,
        margin=dict(t=40, l=40, b=20, r=20),  # Margin of plot
        showlegend=True,
        legend=dict(x=0.9, y=0.98),
        xaxis=dict(
            tickmode='linear',  # Set tick mode to linear
            dtick='M1',  # Set tick frequency to one month (M1)
            tickformat='%b',  # Format tick labels to display only the month abbreviation
            # Set the range of the x-axis to start from August and end with January
            range=['2009-08-01', '2014-01-01']
        ))

    return fig

# ------- Bar chart (sample counts) -------


# @ app.callback(
#     Output('sample_count_bar', 'figure'),
#     [Input('year_range_slider', 'value')]
# )
# def plot_sample_count(year_range):

#     dff = df[df['Year'].between(year_range[0], year_range[1])]

#     counts_per_year = dff['Year'].value_counts().sort_index()

#     fig = px.bar(x=counts_per_year.index, y=counts_per_year.values,
#                  labels={'x': 'Year', 'y': 'Sample Count'},
#                  title='Sample Count per Year')

#     return fig


# start the web application
if __name__ == '__main__':
    app.run_server(debug=True, port=8059)
