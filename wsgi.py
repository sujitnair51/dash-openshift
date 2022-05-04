# -*- coding: utf-8 -*-
# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
from dash import Dash, dcc, html, Input, Output
import folium
import numpy as np
import pandas as pd

app = Dash(__name__)
application = app.server

app.layout = html.Div([
    html.H4("Map of Stations"),
#     html.Div([
#         "Input: ",
#         dcc.Input(id='my-input', value='initial value', type='text')
#     ]),
    html.Br(),
    html.Div(id='my-output'),
    html.Br(),
     html.Div([
        "Latitude: ",
        dcc.Input(id='lat', value=45.5236, type='text')
    ]),
    html.Br(),
     html.Div([
        "Longitude: ",
        dcc.Input(id='long', value=-122.6750, type='text')
    ]),
    html.Div(
      className='max-tile hereMapTile',
      children=[
        dcc.Loading(
          id='loading-map',
          children=[
            html.Iframe(id='hereMap')
            ],
            type='circle'
            )
            ]
            )
  ])


@app.callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='my-input', component_property='value')
)
def update_output_div(input_value):
    return f'Output: {input_value}'



@app.callback(
              Output(component_id='hereMap', component_property='srcDoc'),
              Input(component_id='lat', component_property='value'),
              Input(component_id='long', component_property='value'),
)
def generate_map(lat, long):
        tooltip = 'Click for more info'

        f = folium.Figure(width=1000, height=1000)
        #m=folium.Map([lat[0],lon[0]], zoom_start=4).add_to(f)   

        m=folium.Map(location=[lat, long], zoom_start=13).add_to(f)
        folium.Marker(location=[lat, long],popup="Mt. Hood Meadows",icon=folium.Icon(icon="cloud")).add_to(m)


        #Save the map in a .html file
        m.save("mymapnew.html")
        return open('mymapnew.html', 'r').read()

if __name__ == '__main__':
    app.run_server(debug=True,port=8080)

