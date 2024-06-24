import dash
from dash import dcc, html, Input, Output, State
import dash_leaflet as dl
import pandas as pd
import geopandas as gpd
import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
import pickle
import dash_bootstrap_components as dbc
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from fuzzywuzzy import process
import requests
from io import StringIO
import json
from shapely.geometry import LineString
from branca.colormap import LinearColormap
import folium
from folium.plugins import HeatMap
import os
import branca.colormap as cm
import ast


def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

# DATOS STREET

df_calles_trafico = pd.read_csv("data/street/info_tramos.csv")

df_fallas = pd.read_csv('data/street/datos_13_03_2023_19_03_2023.csv')
df_post_fallas = pd.read_csv('data/street/datos_20_03_2023_26_03_2023.csv')
df_diferencias = pd.read_csv('data/street/calles_mayor_trafico_fallas.csv')

df_fallas_2 = df_fallas.copy(deep=True)
df_post_fallas_2 = df_post_fallas.copy(deep=True)

df_fallas_2['Fecha'] = pd.to_datetime(df_fallas_2['Fecha'])
df_post_fallas_2['Fecha'] = pd.to_datetime(df_post_fallas_2['Fecha'])

df_fallas_2['Hora'] = pd.to_datetime(df_fallas_2['Hora'], format='%H:%M:%S').dt.time
df_post_fallas_2['Hora'] = pd.to_datetime(df_post_fallas_2['Hora'], format='%H:%M:%S').dt.time

df_fallas_2['Datetime'] = df_fallas_2.apply(lambda r: pd.Timestamp.combine(r['Fecha'], r['Hora']), axis=1)
df_post_fallas_2['Datetime'] = df_post_fallas_2.apply(lambda r: pd.Timestamp.combine(r['Fecha'], r['Hora']), axis=1)

df_fallas_2['Día de la semana'] = df_fallas_2['Fecha'].dt.day_name()
df_post_fallas_2['Día de la semana'] = df_post_fallas_2['Fecha'].dt.day_name()

dias_ordenados = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
df_fallas['Día de la semana'] = pd.Categorical(df_fallas['Día de la semana'], categories=dias_ordenados, ordered=True)
df_post_fallas['Día de la semana'] = pd.Categorical(df_post_fallas['Día de la semana'], categories=dias_ordenados, ordered=True)
df_fallas_2['Día de la semana'] = pd.Categorical(df_fallas_2['Día de la semana'], categories=dias_ordenados, ordered=True)
df_post_fallas_2['Día de la semana'] = pd.Categorical(df_post_fallas_2['Día de la semana'], categories=dias_ordenados, ordered=True)

df_rango1_avg = df_fallas_2.groupby('Datetime')['Estat / Estado'].mean().reset_index()
df_rango2_avg = df_post_fallas_2.groupby('Datetime')['Estat / Estado'].mean().reset_index()


fig1, ax1 = plt.subplots(figsize=(14, 7))
ax1.plot(df_rango1_avg['Datetime'].values, df_rango1_avg['Estat / Estado'].values, label='Fallas Week (from 13-03-2023 to 19-03-2023)')
ax1.plot(df_rango2_avg['Datetime'].values, df_rango2_avg['Estat / Estado'].values, label='Post-Fallas week (from 20-03-2023 to 26-03-2023)')
ax1.set_xlabel('Date and Time')
ax1.set_ylabel('Average Traffic Status')
ax1.set_title('Average Traffic Status Evolution')
ax1.legend()
graph1_base64 = fig_to_base64(fig1)
plt.close(fig1)

# Gráfico 2: Serie Temporal del Estado Promedio del Tráfico por Hora del Día
df_fallas_2['Hora'] = pd.to_datetime(df_fallas_2['Hora'], format='%H:%M:%S').dt.hour
df_post_fallas_2['Hora'] = pd.to_datetime(df_post_fallas_2['Hora'], format='%H:%M:%S').dt.hour

df_rango1_avg = df_fallas_2.groupby('Hora')['Estat / Estado'].mean().reset_index()
df_rango2_avg = df_post_fallas_2.groupby('Hora')['Estat / Estado'].mean().reset_index()

df_rango1_avg.columns = ['Hora', 'Estado_promedio']
df_rango2_avg.columns = ['Hora', 'Estado_promedio']

fig2, ax2 = plt.subplots(figsize=(14, 7))
ax2.plot(df_rango1_avg['Hora'].values, df_rango1_avg['Estado_promedio'].values, label='Fallas Week (from 13-03-2023 to 19-03-2023)')
ax2.plot(df_rango2_avg['Hora'].values, df_rango2_avg['Estado_promedio'].values, label='Post-Fallas week (from 20-03-2023 to 26-03-2023)')
ax2.set_xlabel('Time of Day')
ax2.set_ylabel('Average Traffic Status')
ax2.set_title('Time Series of Average Traffic Status by Time of Day')
ax2.legend()
graph2_base64 = fig_to_base64(fig2)
plt.close(fig2)

# Gráfico 3: Heatmap del Estado Promedio del Tráfico en Semana de Fallas
heatmap_data_rango1 = df_fallas_2.pivot_table(values='Estat / Estado', index='Hora', columns='Día de la semana', aggfunc='mean')
fig3, ax3 = plt.subplots(figsize=(14, 7))
sns.heatmap(heatmap_data_rango1, cmap='viridis', cbar_kws={'label': 'Average Status'}, ax=ax3)
ax3.set_title('Heatmap of the Average Traffic Status during the Week of Fallas')
ax3.set_xlabel('Day of the Week')
ax3.set_ylabel('Time of Day')
graph3_base64 = fig_to_base64(fig3)
plt.close(fig3)

# Gráfico 4: Heatmap del Estado Promedio del Tráfico en Semana post-fallas
heatmap_data_rango2 = df_post_fallas_2.pivot_table(values='Estat / Estado', index='Hora', columns='Día de la semana', aggfunc='mean')
fig4, ax4 = plt.subplots(figsize=(14, 7))
sns.heatmap(heatmap_data_rango2, cmap='viridis', cbar_kws={'label': 'Estado Promedio'}, ax=ax4)
ax4.set_title('Heatmap of the Average Traffic Status in the Week after Fallas')
ax4.set_xlabel('Day of the Week')
ax4.set_ylabel('Time of Day')
graph4_base64 = fig_to_base64(fig4)
plt.close(fig4)

# Mapa

df_calles_trafico_2 = df_calles_trafico.copy(deep=True)
df_calles_trafico_2.rename(columns={'Denominacion': 'Denominació / Denominación'}, inplace=True)


df_plot = pd.merge(df_diferencias, df_calles_trafico_2, on='Denominació / Denominación', how='left')
df_plot = df_plot.dropna(subset=['geo_shape'])

m = folium.Map(location=[df_plot['geo_shape'].apply(lambda x: ast.literal_eval(x)['coordinates'][0][1]).mean(), 
                         df_plot['geo_shape'].apply(lambda x: ast.literal_eval(x)['coordinates'][0][0]).mean()], 
               zoom_start=13)

# Crear un colormap
min_diff = df_plot['Diferencia'].min()
max_diff = df_plot['Diferencia'].max()
colormap = cm.LinearColormap(colors=['blue', 'green', 'yellow', 'orange', 'red'], vmin=min_diff, vmax=max_diff)

# Añadir líneas con pop-ups al mapa
for index, row in df_plot.iterrows():
    line = ast.literal_eval(row['geo_shape'])  # Convertir la cadena de texto a una lista de coordenadas
    color = colormap(row['Diferencia'])  # Obtener el color según la diferencia
    folium.GeoJson(
        data={"type": "Feature",
              "geometry": {
                  "type": "LineString",
                  "coordinates": line['coordinates']
              }},
        style_function=lambda x, color=color: {
            'color': color,
            'weight': 5,
            'opacity': 0.8
        },
        popup=folium.Popup(f"Calle: {row['Denominació / Denominación']} \n Diferencia: {row['Diferencia']}")
    ).add_to(m)

# Añadir la leyenda al mapa
colormap.add_to(m)

# Guardar el mapa en un archivo HTML temporal
m.save("map.html")

# Leer el contenido del archivo HTML
with open("map.html", "r", encoding="utf-8") as f:
    folium_html = f.read()

# Borrar el archivo HTML temporal
os.remove("map.html")

# DATOS RUTA

# Cargar datos
G = ox.load_graphml(filepath='data/carpas/valencia_drive.graphml')
gdf = gpd.read_file("data/carpas/gdf_valencia.shp")
gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)

# Inicializar geolocalizador
geolocator = Nominatim(user_agent="dash_app")

# Supongamos que combined_list es la lista combinada
with open("data/carpas/lista_calles", "rb") as fp:
    combined_list = pickle.load(fp)

# Inicializar aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.NavbarBrand("Valencia in Fallas", className="ms-2"),
                    ),
                ],
                align="center",
                className="g-0",
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Home", href="#home", id="tab-home", n_clicks=0, style={'color': 'white'})),
                        dbc.NavItem(dbc.NavLink("General Situation", href="#general-situation", id="tab-general-situation", n_clicks=0, style={'color': 'white'})),
                        dbc.NavItem(dbc.NavLink("How do the Fallas affect your street?", href="#street-information", id="tab-street", n_clicks=0, style={'color': 'white'})),
                        dbc.NavItem(dbc.NavLink("Find the best route", href="#route", id="tab-route", n_clicks=0, style={'color': 'white'})),
                        dbc.NavItem(dbc.NavLink("Real Time Traffic", href="#real-time-traffic", id="tab-real-time-traffic", n_clicks=0, style={'color': 'white'})),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ],
    ),
    color="primary",
    dark=True,
    sticky="top",
    style={'backgroundColor': '#007bff'}
)

# Layout
app.layout = html.Div([
    navbar,
    html.Div(id='tabs-content', className="p-4", style={'min-height': 'calc(100vh - 160px)'}),
])

@app.callback(Output('tabs-content', 'children'),
              [Input('tab-home', 'n_clicks'),
               Input('tab-general-situation', 'n_clicks'),
               Input('tab-street', 'n_clicks'),
               Input('tab-route', 'n_clicks'),
               Input('tab-real-time-traffic', 'n_clicks')])

def render_content(n1, n2, n3, n4, n5):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'tab-home'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'tab-home':
        return html.Div([
            html.H1('Master Valencia\'s Traffic During Fallas', style={'text-align': 'center'}),
            html.Div([
                html.Div([
                    html.P("Each year, during the Fallas celebrations in the city of Valencia, traffic becomes a significant challenge for both residents and visitors. The installation of the traditional fallas, artistic monuments that adorn the streets, causes numerous road closures, complicating vehicular circulation. The influx of tourists and festival activities further exacerbates the situation, leading to significant inconveniences and greater congestion."),
                    html.P("To address these challenges, we present a website designed to provide real-time traffic information in Valencia. This tool is indispensable for planning journeys efficiently, avoiding the most congested areas, and adapting to temporary traffic restrictions. By offering up-to-date traffic data and highlighting areas with significant congestion, users can make informed decisions about their routes, ensuring a smoother driving experience during one of the city's most celebrated, yet traffic-challenged, times of the year."),
                ], style={'width': '60%', 'display': 'inline-block', 'vertical-align': 'top', 'text-align': 'justify'}),
                html.Div([
                    html.Img(src='assets/fallas.jpg', style={'width': '100%', 'border-radius': '5px', 'box-shadow': '0 1px 3px rgba(0, 0, 0, 0.2)'})
                ], style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5%'})
            ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),
            html.Div([
                html.P("The website offers the following services:"),
                html.Ul([
                    html.Li([
                        html.Span("General situation", style={'font-weight': 'bold'}), 
                        ". This section provides an overview of how the Fallas affect traffic in the city of Valencia."
                    ]),
                    html.Li([
                        html.Span("How do the Fallas affect your street", style={'font-weight': 'bold'}), 
                        ". By selecting a street, you can see the traffic conditions during the Fallas week and the week after. This tool helps users identify which streets are more or less affected by the festivities."
                    ]),
                    html.Li([
                        html.Span("Find the best route", style={'font-weight': 'bold'}), 
                        ". Users can enter a starting address and a destination, and our application calculates the best route between the two points, avoiding streets closed due to the Fallas tents."
                    ]),
                    html.Li([
                        html.Span("Real time traffic", style={'font-weight': 'bold'}), 
                        ". Whether it's Fallas season or not, this tool allows users to know the current traffic conditions in the city of Valencia."
                    ]),
                ])
            ], style={'text-align': 'justify', 'margin-top': '20px'})
        ])
    
    elif button_id == 'tab-general-situation':
        return html.Div([
            html.H1('General Situation', style={'text-align': 'center'}),
            html.P("This section provides an overview of how the Fallas affect traffic in the city of Valencia. Detailed information and analyses are provided to help users understand the broader impact of the festivities on vehicular movement throughout the city.",
                style={'text-align': 'justify'}),
            html.P("Before diving into the specifics, it's important to understand that the traffic state is categorized as follows: 0 indicates fluid traffic, 1 indicates dense traffic, 2 indicates congested traffic and 3 indicates that the street is closed. These categories will help you interpret the visualizations presented.",
                style={'text-align': 'justify'}),
            html.Div([
                html.P("The first graph shows the average traffic state over time during the week of Fallas and the week following it. Notice how traffic becomes significantly more congested as the Fallas celebrations approach their peak (March 17, 18 and 19). The increase in traffic congestion is primarily due to the road closures and the influx of visitors. The road closures are implemented to accommodate the various events and installations of Fallas structures, which naturally restricts vehicular movement. Moreover, the influx of visitors from different parts of the country and the world exacerbates the traffic situation, leading to significant congestion. After the Fallas, the traffic state quickly returns to a more fluid state, reflecting the end of the festivities and the reopening of the roads. The rapid return to normal traffic conditions highlights the temporary nature of the disruptions caused by the festival.",
                    style={'text-align': 'justify'}),
                html.Img(src=f'data:image/png;base64,{graph1_base64}', style={'width': '60%', 'border-radius': '5px', 'box-shadow': '0 1px 3px rgba(0, 0, 0, 0.2)', 'margin-top': '20px'}),
            ], style={'text-align': 'center'}),
            html.Div(style={'margin-top': '20px'}),
            html.Div([
                html.P("The second graph presents the average traffic state at different hours of the day during the Fallas week and the post-Fallas week. This temporal series shows that during Fallas, traffic congestion peaks at noon and around 12:00 p.m., likely due to the events and gatherings that occur during these times. These peaks can be attributed to lunchtime activities and midday events, where people gather for social activities, increasing vehicular movement. In contrast, the post-Fallas week exhibits a more stable and fluid traffic state throughout the day, with minor variations. The more stable traffic conditions during the post-Fallas week indicate a return to normalcy, where daily commuting patterns are less disrupted by festivities and road closures.",
                    style={'text-align': 'justify'}),
                html.Img(src=f'data:image/png;base64,{graph2_base64}', style={'width': '60%', 'border-radius': '5px', 'box-shadow': '0 1px 3px rgba(0, 0, 0, 0.2)', 'margin-top': '20px'}),
            ], style={'text-align': 'center'}),
            html.Div([
                html.P("The heatmaps provide a more detailed look at traffic patterns throughout the day for both the Fallas week and the post-Fallas week. The color intensity represents the traffic state, with darker colors indicating less congested traffic. During the Fallas week, congestion is notably higher, especially from Friday afternoon and throughout the weekend, even on Monday (March 19) in the early morning, when the Fallas are burned. From this last statement, it follows that these periods of high congestion are directly correlated with the scheduled events and the increased movement of people attending these festivities. In contrast, the post-Fallas week shows a much more fluid traffic state, indicating that the city returns to normal traffic conditions. The reduction in traffic congestion after the Fallas highlights the significant impact that these events have on the city's traffic flow.",
                    style={'text-align': 'justify', 'margin-top': '20px'}),
            ], style={'text-align': 'center'}),
            html.Div([
                html.Div([
                    html.Img(src=f'data:image/png;base64,{graph3_base64}', style={'width': '90%', 'border-radius': '5px', 'box-shadow': '0 1px 3px rgba(0, 0, 0, 0.2)', 'margin-top': '20px'}),
                ], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top', 'text-align': 'center'}),
                html.Div([
                    html.Img(src=f'data:image/png;base64,{graph4_base64}', style={'width': '90%', 'border-radius': '5px', 'box-shadow': '0 1px 3px rgba(0, 0, 0, 0.2)', 'margin-top': '20px'}),
                ], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top', 'text-align': 'center'}),
            ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),
            html.Div(style={'margin-top': '20px'}),
            html.Div([
                html.P([
                    "The final element is an interactive map that visualizes the differences in traffic conditions between the Fallas week and the subsequent week. This map highlights the streets that experience the most significant changes in traffic congestion. Streets with the highest increase in traffic during Fallas are marked with more intense colors, indicating a greater difference compared to the following week. This visual representation allows for a clearer understanding of how specific areas in Valencia are impacted by the festivities. The colormap legend helps interpret the intensity of the differences, providing a useful tool for both residents and city planners to identify and manage high-traffic areas during major events. If you want to know the information of a street without having to look it up on the map, visit the section ",
                    html.Span("How do the Fallas affect your street?", style={'font-weight': 'bold'}),
                    "."
                ], style={'text-align': 'justify'}),
                html.Iframe(srcDoc=folium_html, width='80%', height='600px', style={'border': 'none', 'margin-top': '20px'}),
            ], style={'text-align': 'center'}),
        ])
    
    elif button_id == 'tab-street':
        return html.Div([
            html.H1('How do the Fallas affect your street?', style={'text-align': 'center'}),
            html.P("Here you can find detailed information about the streets of Valencia.", style={'text-align': 'center'}),
            html.P("It's important to understand that the traffic state is categorized as follows: 0 indicates fluid traffic, 1 indicates dense traffic, and 2 indicates congested traffic. 3 indicates that the street is closed.", style={'text-align': 'center'}),
            dcc.Dropdown(
                id='street-dropdown',
                options=[{'label': calle, 'value': calle} for calle in df_calles_trafico['Denominacion'].unique()],
                placeholder='Seleccione una calle',
                style={'width': '100%'},
                searchable=True
            ),
            html.Div(id='street-content')
        ])
    elif button_id == 'tab-route':
        return html.Div([
            html.H1("Shortest Route Avoiding Tents in Valencia", style={'text-align': 'center'}),
            html.Div([
                # Left side with description and input boxes
                html.Div([
                    html.P(
                        "We understand that the Fallas tents can cause significant inconveniences when driving due to street closures. "
                        "Google Maps does not provide information on whether a tent is blocking a street, which can make navigation difficult. "
                        "Our application helps you find the best route between two points without passing through any closed streets caused by the Fallas tents. "
                        "Simply enter the origin and destination addresses in the fields below and generate the route. "
                        "This tool ensures that you avoid any disruptions caused by the tents, making your travel in Valencia smoother and more efficient. "
                        "Take advantage of this specialized service during the Fallas festival to save time and avoid unnecessary detours."
                    ),
                    html.Div([
                        dcc.Dropdown(
                            id='origin-address',
                            options=[{'label': i, 'value': i} for i in combined_list],
                            placeholder='Origin Address',
                            style={'width': '100%'},
                            searchable=True
                        ),
                    ], style={'margin-bottom': '10px'}),
                    html.Div([
                        dcc.Dropdown(
                            id='destination-address',
                            options=[{'label': i, 'value': i} for i in combined_list],
                            placeholder='Destination Address',
                            style={'width': '100%'},
                            searchable=True
                        ),
                    ], style={'margin-bottom': '10px'}),
                    html.Button('Show Route', id='show-route-button', n_clicks=0, className='btn btn-primary', style={'margin-top': '10px'}),
                ], style={'width': '35%', 'display': 'inline-block', 'padding-right': '20px', 'vertical-align': 'top'}),

                # Right side with the map
                html.Div([
                    dl.Map(center=[39.4699, -0.3763], zoom=12, id='map', style={'width': '100%', 'height': '500px'}, children=[
                        dl.TileLayer(),
                        dl.GeoJSON(data=gdf.__geo_interface__, options=dict(style=dict(color='red', weight=5, fillOpacity=0.6)))
                    ])
                ], style={'width': '60%', 'display': 'inline-block', 'vertical-align': 'top'}),
            ], style={'display': 'flex', 'justify-content': 'space-between'})
        ])
    
    elif button_id == 'tab-real-time-traffic':
        return html.Div([
            html.H1('Real-Time Traffic Information', style={'text-align': 'center'}),
            html.P("You are in Fallas and you want to know the traffic conditions in the city of Valencia. "
                   "Even if you are not, you might want to know the current traffic situation, be prepared for any eventuality in your trip, "
                   "or you are simply curious about the current traffic conditions in the city. "
                   "Press this button to get real-time information and ensure that your movements are as smooth as possible. "
                   "With this tool, you will have access to the latest data on traffic conditions in Valencia, allowing you to better plan your trip "
                   "and avoid congested areas."),
            html.Button('Get Traffic Now', id='show-traffic-button', n_clicks=0, className='btn btn-primary', style={'margin': '20px auto', 'display': 'block'}),
            html.Div(id='real-time-traffic-map', style={'height': '500px'})
        ])



@app.callback(
    Output('street-content', 'children'),
    [Input('street-dropdown', 'value')]
)
def update_street_content(selected_street):
    if selected_street is None:
        return html.Div()

    # Utilizar fuzzywuzzy para encontrar la opción más parecida
    closest_match_fallas = process.extractOne(selected_street, df_fallas['Denominació / Denominación'].unique())[0]
    closest_match_post_fallas = process.extractOne(selected_street, df_post_fallas['Denominació / Denominación'].unique())[0]

    # Filtrar los datos por la opción más parecida
    df_fallas_filtered = df_fallas.loc[df_fallas['Denominació / Denominación'] == closest_match_fallas]
    df_post_fallas_filtered = df_post_fallas.loc[df_post_fallas['Denominació / Denominación'] == closest_match_post_fallas]

    # Convertir la columna 'Hora' a horas
    df_fallas_filtered.loc[:, 'Hora'] = pd.to_datetime(df_fallas_filtered['Hora'], format='%H:%M:%S').dt.hour
    df_post_fallas_filtered.loc[:, 'Hora'] = pd.to_datetime(df_post_fallas_filtered['Hora'], format='%H:%M:%S').dt.hour

    # Calcular el estado promedio de tráfico
    estado_promedio_fallas = df_fallas_filtered['Estat / Estado'].mean()
    estado_promedio_post_fallas = df_post_fallas_filtered['Estat / Estado'].mean()

    # Calcular la diferencia entre semanas de Fallas y post-Fallas
    diferencia = estado_promedio_fallas - estado_promedio_post_fallas 
    promedio_diferencias = df_diferencias['Diferencia'].mean()

    # Determinar el color según la diferencia
    if -2 <= diferencia < -1:
        color = 'darkgreen'
    elif -1 <= diferencia < 0:
        color = 'lightgreen'
    elif 0 <= diferencia < 1:
        color = 'yellow'
    elif 1 <= diferencia < 2:
        color = 'orange'
    elif 2 <= diferencia < 3:
        color = 'red'
    else:
        color = 'grey'  # Para diferencias fuera de los rangos especificados

    # Crear los gráficos de series temporales
    fallas_avg_by_hour = df_fallas_filtered.groupby('Hora')['Estat / Estado'].mean().reset_index()
    post_fallas_avg_by_hour = df_post_fallas_filtered.groupby('Hora')['Estat / Estado'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(fallas_avg_by_hour['Hora'].values, fallas_avg_by_hour['Estat / Estado'].values, label='Fallas Week', color='blue')
    ax.plot(post_fallas_avg_by_hour['Hora'].values, post_fallas_avg_by_hour['Estat / Estado'].values, label='Post-Fallas Week', color='orange')
    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel('Average Traffic State')
    ax.set_title(f'Hourly Traffic State in {selected_street}')
    ax.legend()

    # Convertir el gráfico a una imagen en base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    plt.close(fig)

    if estado_promedio_fallas == 3:
        return html.Div([
            html.H4('The street is closed during Fallas', style={'font-weight': 'bold', 'color': 'red', 'text-align': 'center', 'margin-top': '20px'}),
            html.Div([
                html.Img(src=f'data:image/png;base64,{plot_url}', style={'width': '35%', 'border-radius': '5px', 'box-shadow': '0 1px 3px rgba(0, 0, 0, 0.2)'})
            ], style={'text-align': 'center', 'padding': '10px', 'margin-top': '20px'})
        ])
    else:
        comparacion = "more" if diferencia > promedio_diferencias else "less"

        return html.Div([
            html.Div([
                html.Div([
                    html.H4('Average Traffic State during Fallas Week', style={'font-weight': 'bold'}),
                    html.P(f'{estado_promedio_fallas:.2f}', className='display-4'),
                ], className='p-3 mb-3', style={'background-color': '#f8f9fa', 'border-radius': '5px', 'box-shadow': '0 1px 3px rgba(0, 0, 0, 0.2)', 'text-align': 'center'}),
                html.Div("-", style={'font-size': '32px', 'margin': '0 20px', 'align-self': 'center'}),
                html.Div([
                    html.H4('Average Traffic State during Post-Fallas Week', style={'font-weight': 'bold'}),
                    html.P(f'{estado_promedio_post_fallas:.2f}', className='display-4'),
                ], className='p-3 mb-3', style={'background-color': '#f8f9fa', 'border-radius': '5px', 'box-shadow': '0 1px 3px rgba(0, 0, 0, 0.2)', 'text-align': 'center'}),
                html.Div("=", style={'font-size': '32px', 'margin': '0 20px', 'align-self': 'center'}),
                html.Div([
                    html.H4('Difference', style={'font-weight': 'bold'}),
                    html.P(f'{diferencia:.2f}', className='display-4'),
                ], className='p-3 mb-3', style={'background-color': color, 'border-radius': '5px', 'box-shadow': '0 1px 3px rgba(0, 0, 0, 0.2)', 'text-align': 'center'}),
            ], className='d-flex justify-content-around flex-wrap', style={'margin-top': '20px'}),
            html.Div([
                html.H4('Comparison with Average Difference', style={'font-weight': 'bold'}),
                html.P(['Average Difference: ', html.Span(f'{promedio_diferencias:.2f}', style={'font-weight': 'bold'})]),
                html.P([
                    f'The street {selected_street} is ',
                    html.Span(comparacion, style={'font-weight': 'bold'}),
                    ' affected by traffic than the average during Fallas.'
                ]),
            ], className='p-3 mb-3', style={'background-color': '#f8f9fa', 'border-radius': '5px', 'box-shadow': '0 1px 3px rgba(0, 0, 0, 0.2)', 'text-align': 'center'}),
            html.P('This is the general situation. Below you can see a graph showing the hourly average traffic state over the two weeks.', style={'text-align': 'center', 'margin-top': '20px'}),
            html.Div([
                html.Img(src=f'data:image/png;base64,{plot_url}', style={'width': '35%', 'border-radius': '5px', 'box-shadow': '0 1px 3px rgba(0, 0, 0, 0.2)'})
            ], style={'text-align': 'center', 'padding': '10px', 'margin-top': '20px'})
        ])

def add_route_to_map(route, color='blue'):
    route_nodes = gdf_nodes.loc[route]
    return dl.Polyline(
        positions=[(point.y, point.x) for point in route_nodes.geometry],
        color=color,
        weight=5,
        opacity=0.8
    )

def find_route(G, point_a, point_b):
    orig_node = ox.distance.nearest_nodes(G, X=point_a[1], Y=point_a[0])
    dest_node = ox.distance.nearest_nodes(G, X=point_b[1], Y=point_b[0])
    try:
        route = nx.shortest_path(G, orig_node, dest_node, weight='length')
        return route
    except nx.NetworkXNoPath:
        nearest_dest_node = ox.distance.nearest_nodes(G, X=point_b[1], Y=point_b[0])
        return nx.shortest_path(G, orig_node, nearest_dest_node, weight='length')

def add_markers(point_a, point_b):

    icon_a = {
        "iconUrl": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",
        "iconSize": [25, 41],  # tamaño del icono
        "iconAnchor": [12, 41],  # punto del icono que se coloca en la lat/lon
        "popupAnchor": [1, -34],  # donde debe aparecer el pop-up en relación al icono
        "shadowUrl": "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
        "shadowSize": [41, 41]
    }
    icon_b = {
        "iconUrl": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
        "iconSize": [25, 41],
        "iconAnchor": [12, 41],
        "popupAnchor": [1, -34],
        "shadowUrl": "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
        "shadowSize": [41, 41]
    }

    marker_a = dl.Marker(position=point_a, children=dl.Tooltip('Origen'), icon = icon_a)
    marker_b = dl.Marker(position=point_b, children=dl.Tooltip('Destino'), icon = icon_b)
    return [marker_a, marker_b]

@app.callback(
    Output('map', 'children'),
    [Input('show-route-button', 'n_clicks')],
    [State('origin-address', 'value'), State('destination-address', 'value')]
)
def update_map(n_clicks, origin_address, destination_address):
    if n_clicks > 0:
        if not origin_address or not destination_address:
            return [dl.TileLayer(), dl.GeoJSON(data=gdf.__geo_interface__, options=dict(style=dict(color='red', weight=5, fillOpacity=0.6)))]

        # Agregar información adicional a las direcciones para geocodificación
        full_origin_address = origin_address + ", València, Comarca de València, València / Valencia, Comunitat Valenciana, España"
        full_destination_address = destination_address + ", València, Comarca de València, València / Valencia, Comunitat Valenciana, España"

        location_a = geolocator.geocode(full_origin_address)
        location_b = geolocator.geocode(full_destination_address)

        if location_a and location_b:
            point_a = (location_a.latitude, location_a.longitude)
            point_b = (location_b.latitude, location_b.longitude)

            try:
                route = find_route(G, point_a, point_b)
                polyline = add_route_to_map(route)
                markers = add_markers(point_a, point_b)
                return [
                    dl.TileLayer(),
                    polyline,
                    *markers,
                    dl.GeoJSON(data=gdf.__geo_interface__, options=dict(style=dict(color='red', weight=5, fillOpacity=0.6)))
                ]
            except nx.NetworkXNoPath:
                return [dl.TileLayer(), dl.GeoJSON(data=gdf.__geo_interface__, options=dict(style=dict(color='red', weight=5, fillOpacity=0.6)))]
        else:
            return [dl.TileLayer(), dl.GeoJSON(data=gdf.__geo_interface__, options=dict(style=dict(color='red', weight=5, fillOpacity=0.6)))]
    else:
        return [dl.TileLayer(), dl.GeoJSON(data=gdf.__geo_interface__, options=dict(style=dict(color='red', weight=5, fillOpacity=0.6)))]



def get_real_time_traffic_data():
    url = "https://valencia.opendatasoft.com/explore/dataset/estat-transit-temps-real-estado-trafico-tiempo-real/download/?format=csv&timezone=Europe/Berlin&lang=es&use_labels_for_header=true&csv_separator=%3B"
    response = requests.get(url)
    response.raise_for_status()
    csv_content = response.content.decode('utf-8')
    df = pd.read_csv(StringIO(csv_content), sep=';')
    
    def unificar_estado(estado):
        if estado in [0, 5]:
            return 0  # Fluido
        elif estado in [1, 6]:
            return 1  # Denso
        elif estado in [2, 7]:
            return 2  # Congestionado
        elif estado in [3, 8]:
            return 3  # Cortado
        elif estado in [4, 9]:
            return 4  # Sin datos
        else:
            return estado
    
    def convertir_a_linestring(geojson_str):
        geojson_data = json.loads(geojson_str)
        return LineString(geojson_data['coordinates'])
    
    df['Estat / Estado'] = df['Estat / Estado'].apply(unificar_estado)
    df['geometry'] = df['geo_shape'].apply(convertir_a_linestring)
    
    # Convertir DataFrame a GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    
    return gdf

@app.callback(
    Output('real-time-traffic-map', 'children'),
    [Input('show-traffic-button', 'n_clicks')]
)
def show_real_time_traffic(n_clicks):
    if n_clicks > 0:
        gdf = get_real_time_traffic_data()
        estado_weights = {
            0: 0.2,  # Fluido
            1: 0.5,  # Denso
            2: 1.0,  # Congestionado
        }
        
        # Crear datos de calor
        heat_data = []
        for idx, row in gdf.iterrows():
            geom = row['geometry']
            estado = row['Estat / Estado']
            weight = estado_weights.get(estado, 0.1)
            if geom.geom_type == 'LineString':
                for coord in geom.coords:
                    lat, lon = coord[1], coord[0]
                    heat_data.append([lat, lon, weight])
        
        # Crear el colormap personalizado
        color_map = LinearColormap(['blue', 'green', 'yellow', 'red'], vmin=0, vmax=1)
        
        # Crear el mapa de Folium
        m = folium.Map(location=[39.4699, -0.3763], zoom_start=12)
        HeatMap(heat_data, gradient={i / 20: color_map.rgb_hex_str(i / 20) for i in range(21)}, max_opacity=0.8, radius=10).add_to(m)
        color_map.caption = 'Traffic status'
        color_map.add_to(m)
        
        # Guardar el mapa en un archivo HTML temporal
        m.save("folium_map.html")
        
        # Leer el contenido del archivo HTML
        with open("folium_map.html", "r", encoding="utf-8") as f:
            folium_html = f.read()
        
        # Borrar el archivo HTML temporal
        os.remove("folium_map.html")
        
        return html.Iframe(srcDoc=folium_html, width="100%", height="500")
    else:
        return html.Div()  # Devuelve una vista vacía si no se ha pulsado el botón

    
if __name__ == '__main__':
    app.run_server(debug=True, port = "8050", host="0.0.0.0")