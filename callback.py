
import copy
import pathlib
import urllib.request
import dash
import math
import datetime as dt
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, ClientsideFunction
import folium
from da import get_dataframe
import io
import json
import folium
import openrouteservice
from openrouteservice import convert
import dash_bootstrap_components as dbc
from layouts.header import navbar
from layouts.content import content as page_content
from layouts.sidebar import sidebar
from content.station import station
from content.trip import trip

from wsgi import app

# Multi-dropdown options
from controls import PROVINCE, PRODUCT_TYPES
# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# Helper functions
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return station
    elif pathname == "/trips":
        return trip
    elif pathname == "/page-2":
        return html.P("Oh cool, this is page 2!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
)
# Radio -> multi
@app.callback(
    Output("province", "value"), [Input("province_selector", "value")]
)
def display_province(selector):
    if selector == "all":
        return list(PROVINCE.keys())
    elif selector == "active":
        return ["ON"]
    return []


# Radio -> multi
@app.callback(Output("product_types", "value"), [Input("product_type_selector", "value")])
def display_type(selector):
    if selector == "all":
        return list(PRODUCT_TYPES.keys())
    # elif selector == "productive":
    #     return ["GD", "GE", "GW", "IG", "IW", "OD", "OE", "OW"]
    return []


# Slider -> count graph
@app.callback(Output("year_slider", "value"), [Input("count_graph", "selectedData")])
def update_year_slider(count_graph_selected):

    if count_graph_selected is None:
        return [1990, 2010]

    nums = [int(point["pointNumber"]) for point in count_graph_selected["points"]]
    return [min(nums) + 1960, max(nums) + 1961]


@app.callback(
              Output(component_id='hereMap', component_property='srcDoc'),
              Input(component_id='hour_slider', component_property='value'),
              Input(component_id='province', component_property='value'),
)
def generate_map(hr, province):
    Location = get_dataframe()
    tooltip = 'Click for more info'
    lat = 43.763333
    long = -79.708889
    f = folium.Figure(width=1000, height=1000)
      
    m=folium.Map(location=[lat, long], zoom_start=13).add_to(f)
   
   
    for i , r in Location.iterrows():
        html = '''<h6>Gas Station</h6><br>Name:'''+r.loc["LocationName"]+'''<br>Postal Code:'''+r.loc["PostalCode"]
        iframe = folium.IFrame(html,
                       width=200,
                       height=100)
        popup = folium.Popup(iframe,
                     max_width=200)
        # popup = folium.Popup("Hello")
        
        if r["Province"] in province:

            if hr[0] <= r["RunOut"] <=hr[1]:
                folium.Marker(location=[r["Latitude"], r["Longitude"]], popup=popup, tooltip=tooltip, icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
             
            else:
                # popup.add_child(v)
                folium.Marker(location=[r["Latitude"], r["Longitude"]], popup=popup, tooltip=tooltip, icon=folium.Icon(color="green", icon="info-sign")).add_to(m)
                
    
    #Save the map in a .html file
    sw = Location[['Latitude', 'Longitude']].min().values.tolist()
    ne = Location[['Latitude', 'Longitude']].max().values.tolist()
    m.fit_bounds([sw, ne]) 
    m.save("mymapnew.html")
    return open('mymapnew.html', 'r').read()

@app.callback(
              Output(component_id='route-map', component_property='srcDoc'),
              [Input("url", "pathname")]
)
def generate_route_map(pathname):
    if pathname == "/trips":
        client = openrouteservice.Client(key='5b3ce3597851110001cf6248a68ca6687fe64109b956e946bb02b36b')

        coords = ((80.21787585263182,6.025423265401452),(80.23990263756545,6.018498276842677))
        res = client.directions(coords)
        geometry = client.directions(coords)['routes'][0]['geometry']
        decoded = convert.decode_polyline(geometry)

        distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['distance']/1000,1))+" Km </strong>" +"</h4></b>"
        duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['duration']/60,1))+" Mins. </strong>" +"</h4></b>"

        m = folium.Map(location=[6.074834613830474, 80.25749815575348],zoom_start=10, control_scale=True,tiles="cartodbpositron")
        folium.GeoJson(decoded).add_child(folium.Popup(distance_txt+duration_txt,max_width=300)).add_to(m)

        folium.Marker(
                location=list(coords[0][::-1]),
                popup="Galle fort",
                icon=folium.Icon(color="green"),
            ).add_to(m)

        folium.Marker(
                location=list(coords[1][::-1]),
                popup="Jungle beach",
                icon=folium.Icon(color="red"),
            ).add_to(m)

        m.save("mymapnew.html")
        return open('mymapnew.html', 'r').read()