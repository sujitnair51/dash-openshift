# Import required libraries
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
from folium import features
import vincent
from vincent import Bar
import openrouteservice
from openrouteservice import convert

# Multi-dropdown options
from controls import COUNTIES, WELL_STATUSES, WELL_TYPES, WELL_COLORS, PROVINCE, PRODUCT_TYPES
#----sample data---------
data = '''
State   Type    lat         lng         Total
Alabama Brand   32.318231   -86.902298  100
Alabama Generic 32.318231   -86.902298  200
Alabama OTC     32.318231   -86.902298  300
Alabama RX      32.318231   -86.902298  400
Alabama Total   32.318231   -86.902298  500
'''
alabama_data = pd.read_csv(io.StringIO(data), delim_whitespace=True)

alabama_data.set_index('Type', inplace=True)
#---------------
# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "DO Optimization"
server = app.server
application = app.server

# Create controls
county_options = [
    {"label": str(COUNTIES[county]), "value": str(county)} for county in COUNTIES
]

well_status_options = [
    {"label": str(WELL_STATUSES[well_status]), "value": str(well_status)}
    for well_status in WELL_STATUSES
]

province_options = [
    {"label": str(PROVINCE[province]), "value": str(province)}
    for province in PROVINCE
]

product_type_options = [
    {"label": str(PRODUCT_TYPES[product_type]), "value": str(product_type)}
    for product_type in PRODUCT_TYPES
]

well_type_options = [
    {"label": str(WELL_TYPES[well_type]), "value": str(well_type)}
    for well_type in WELL_TYPES
]



df = None
dataset = None

refuel_stations = pd.DataFrame([])


layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("dash-logo.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Route Optimization Dashboard",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Demand Overview", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Learn More", id="learn-more-button"),
                            href="https://plot.ly/dash/pricing/",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Filter by Fuel Run out time (in hours):",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="hour_slider",
                            min=0,
                            max=118,
                            step=1,
                            value=[24, 32],
                            marks={
                                0: {'label': '0 hrs', 'style': {'color': '#77b0b1'}},
                                24: {'label': '24 hrs'},
                                48: {'label': '48 hrs'},
                                72: {'label': '72 hrs'},
                                94: {'label': '94 hrs'},
                                118: {'label': '118 hrs', 'style': {'color': '#f50'}}
                                },
                            tooltip={"placement": "bottom", "always_visible": True},
                            className="dcc_control",
                        ),
                        html.P("Filter by Region:", className="control_label"),
                        dcc.RadioItems(
                            id="province_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Ontario", "value": "active"},
                                {"label": "Atlantic", "value": "custom"},
                            ],
                            value="active",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="province",
                            options=province_options,
                            multi=True,
                            value=list(PROVINCE.keys()),
                            className="dcc_control",
                        ),
                        html.P("Filter by Product type:", className="control_label"),
                        dcc.RadioItems(
                            id="product_type_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                # {"label": "Petrol", "value": "productive"},
                                # {"label": "Diesel ", "value": "custom"},
                            ],
                            value="productive",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="product_types",
                            options=product_type_options,
                            multi=True,
                            value=list(PRODUCT_TYPES.keys()),
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="well_text"), html.P("No. of Gas Stations")],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="gasText"), html.P("Products in demand")],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="oilText"), html.P("Nmber of Trucks available")],
                                    id="oil",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="waterText"), html.P("Some Other parameter")],
                                    id="water",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        #location map
                        html.Div(
                            [dcc.Loading(
                                id="loading-map",
                                children=[html.Iframe(id='hereMap', style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"})], type='circle')],

                            id="countGraphContainer",
                            className="pretty_container",
                            # [dcc.Graph(id="count_graph")],
                            # id="countGraphContainer",
                            # className="pretty_container",
                        ),


                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [dcc.Loading(
                id="loading-map2",
                children=[html.Iframe(id='route-map', style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"})], type='circle')],

            id="countGraphContainer2",
            className="pretty_container",
            # [dcc.Graph(id="count_graph")],
            # id="countGraphContainer",
            # className="pretty_container",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# Helper functions
def human_format(num):
    if num == 0:
        return "0"

    magnitude = int(math.log(num, 1000))
    mantissa = str(int(num / (1000 ** magnitude)))
    return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]


def filter_dataframe(df, well_statuses, well_types, year_slider):
    dff = df[
        df["Well_Status"].isin(well_statuses)
        & df["Well_Type"].isin(well_types)
        & (df["Date_Well_Completed"] > dt.datetime(year_slider[0], 1, 1))
        & (df["Date_Well_Completed"] < dt.datetime(year_slider[1], 1, 1))
    ]
    return dff


def produce_individual(api_well_num):
    try:
        points[api_well_num]
    except:
        return None, None, None, None

    index = list(
        range(min(points[api_well_num].keys()), max(points[api_well_num].keys()) + 1)
    )
    gas = []
    oil = []
    water = []

    for year in index:
        try:
            gas.append(points[api_well_num][year]["Gas Produced, MCF"])
        except:
            gas.append(0)
        try:
            oil.append(points[api_well_num][year]["Oil Produced, bbl"])
        except:
            oil.append(0)
        try:
            water.append(points[api_well_num][year]["Water Produced, bbl"])
        except:
            water.append(0)

    return index, gas, oil, water


def produce_aggregate(selected, year_slider):

    index = list(range(max(year_slider[0], 1985), 2016))
    gas = []
    oil = []
    water = []

    for year in index:
        count_gas = 0
        count_oil = 0
        count_water = 0
        for api_well_num in selected:
            try:
                count_gas += points[api_well_num][year]["Gas Produced, MCF"]
            except:
                pass
            try:
                count_oil += points[api_well_num][year]["Oil Produced, bbl"]
            except:
                pass
            try:
                count_water += points[api_well_num][year]["Water Produced, bbl"]
            except:
                pass
        gas.append(count_gas)
        oil.append(count_oil)
        water.append(count_water)

    return index, gas, oil, water


# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("count_graph", "figure")],
)


@app.callback(
    Output("aggregate_data", "data"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
    ],
)
def update_production_text(well_statuses, well_types, year_slider):

    dff = filter_dataframe(df, well_statuses, well_types, year_slider)
    selected = dff["API_WellNo"].values
    index, gas, oil, water = produce_aggregate(selected, year_slider)
    return [human_format(sum(gas)), human_format(sum(oil)), human_format(sum(water))]


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


# Selectors -> well text
@app.callback(
    Output("well_text", "children"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
    ],
)
def update_well_text(well_statuses, well_types, year_slider):

    dff = filter_dataframe(df, well_statuses, well_types, year_slider)
    return dff.shape[0]


@app.callback(
    [
        Output("gasText", "children"),
        Output("oilText", "children"),
        Output("waterText", "children"),
    ],
    [Input("aggregate_data", "data")],
)
def update_text(data):
    return data[0] + " mcf", data[1] + " bbl", data[2] + " bbl"


# Selectors -> main graph
@app.callback(
    Output("main_graph", "figure"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
    ],
    [State("lock_selector", "value"), State("main_graph", "relayoutData")],
)
def make_main_figure(
    well_statuses, well_types, year_slider, selector, main_graph_layout
):

    dff = filter_dataframe(df, well_statuses, well_types, year_slider)

    traces = []
    for well_type, dfff in dff.groupby("Well_Type"):
        trace = dict(
            type="scattermapbox",
            lon=dfff["Surface_Longitude"],
            lat=dfff["Surface_latitude"],
            text=dfff["Well_Name"],
            customdata=dfff["API_WellNo"],
            name=WELL_TYPES[well_type],
            marker=dict(size=4, opacity=0.6),
        )
        traces.append(trace)

    # relayoutData is None by default, and {'autosize': True} without relayout action
    if main_graph_layout is not None and selector is not None and "locked" in selector:
        if "mapbox.center" in main_graph_layout.keys():
            lon = float(main_graph_layout["mapbox.center"]["lon"])
            lat = float(main_graph_layout["mapbox.center"]["lat"])
            zoom = float(main_graph_layout["mapbox.zoom"])
            layout["mapbox"]["center"]["lon"] = lon
            layout["mapbox"]["center"]["lat"] = lat
            layout["mapbox"]["zoom"] = zoom

    figure = dict(data=traces, layout=layout)
    return figure


# Main graph -> individual graph
@app.callback(Output("individual_graph", "figure"), [Input("main_graph", "hoverData")])
def make_individual_figure(main_graph_hover):

    layout_individual = copy.deepcopy(layout)

    if main_graph_hover is None:
        main_graph_hover = {
            "points": [
                {"curveNumber": 4, "pointNumber": 569, "customdata": 31101173130000}
            ]
        }

    chosen = [point["customdata"] for point in main_graph_hover["points"]]
    index, gas, oil, water = produce_individual(chosen[0])

    if index is None:
        annotation = dict(
            text="No data available",
            x=0.5,
            y=0.5,
            align="center",
            showarrow=False,
            xref="paper",
            yref="paper",
        )
        layout_individual["annotations"] = [annotation]
        data = []
    else:
        data = [
            dict(
                type="scatter",
                mode="lines+markers",
                name="Gas Produced (mcf)",
                x=index,
                y=gas,
                line=dict(shape="spline", smoothing=2, width=1, color="#fac1b7"),
                marker=dict(symbol="diamond-open"),
            ),
            dict(
                type="scatter",
                mode="lines+markers",
                name="Oil Produced (bbl)",
                x=index,
                y=oil,
                line=dict(shape="spline", smoothing=2, width=1, color="#a9bb95"),
                marker=dict(symbol="diamond-open"),
            ),
            dict(
                type="scatter",
                mode="lines+markers",
                name="Water Produced (bbl)",
                x=index,
                y=water,
                line=dict(shape="spline", smoothing=2, width=1, color="#92d8d8"),
                marker=dict(symbol="diamond-open"),
            ),
        ]
        layout_individual["title"] = dataset[chosen[0]]["Well_Name"]

    figure = dict(data=data, layout=layout_individual)
    return figure


# Selectors, main graph -> aggregate graph
@app.callback(
    Output("aggregate_graph", "figure"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
        Input("main_graph", "hoverData"),
    ],
)
def make_aggregate_figure(well_statuses, well_types, year_slider, main_graph_hover):

    layout_aggregate = copy.deepcopy(layout)

    if main_graph_hover is None:
        main_graph_hover = {
            "points": [
                {"curveNumber": 4, "pointNumber": 569, "customdata": 31101173130000}
            ]
        }

    chosen = [point["customdata"] for point in main_graph_hover["points"]]
    well_type = dataset[chosen[0]]["Well_Type"]
    dff = filter_dataframe(df, well_statuses, well_types, year_slider)

    selected = dff[dff["Well_Type"] == well_type]["API_WellNo"].values
    index, gas, oil, water = produce_aggregate(selected, year_slider)

    data = [
        dict(
            type="scatter",
            mode="lines",
            name="Gas Produced (mcf)",
            x=index,
            y=gas,
            line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
        ),
        dict(
            type="scatter",
            mode="lines",
            name="Oil Produced (bbl)",
            x=index,
            y=oil,
            line=dict(shape="spline", smoothing="2", color="#849E68"),
        ),
        dict(
            type="scatter",
            mode="lines",
            name="Water Produced (bbl)",
            x=index,
            y=water,
            line=dict(shape="spline", smoothing="2", color="#59C3C3"),
        ),
    ]
    layout_aggregate["title"] = "Aggregate: " + WELL_TYPES[well_type]

    figure = dict(data=data, layout=layout_aggregate)
    return figure


# Selectors, main graph -> pie graph
@app.callback(
    Output("pie_graph", "figure"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
    ],
)
def make_pie_figure(well_statuses, well_types, year_slider):

    layout_pie = copy.deepcopy(layout)

    dff = filter_dataframe(df, well_statuses, well_types, year_slider)

    selected = dff["API_WellNo"].values
    index, gas, oil, water = produce_aggregate(selected, year_slider)

    aggregate = dff.groupby(["Well_Type"]).count()

    data = [
        dict(
            type="pie",
            labels=["Gas", "Oil", "Water"],
            values=[sum(gas), sum(oil), sum(water)],
            name="Production Breakdown",
            text=[
                "Total Gas Produced (mcf)",
                "Total Oil Produced (bbl)",
                "Total Water Produced (bbl)",
            ],
            hoverinfo="text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8"]),
            domain={"x": [0, 0.45], "y": [0.2, 0.8]},
        ),
        dict(
            type="pie",
            labels=[WELL_TYPES[i] for i in aggregate.index],
            values=aggregate["API_WellNo"],
            name="Well Type Breakdown",
            hoverinfo="label+text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(colors=[WELL_COLORS[i] for i in aggregate.index]),
            domain={"x": [0.55, 1], "y": [0.2, 0.8]},
        ),
    ]
    layout_pie["title"] = "Production Summary: {} to {}".format(
        year_slider[0], year_slider[1]
    )
    layout_pie["font"] = dict(color="#777777")
    layout_pie["legend"] = dict(
        font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
    )

    figure = dict(data=data, layout=layout_pie)
    return figure


# Selectors -> count graph
@app.callback(
    Output("count_graph", "figure"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("year_slider", "value"),
    ],
)
def make_count_figure(well_statuses, well_types, year_slider):

    layout_count = copy.deepcopy(layout)

    dff = filter_dataframe(df, well_statuses, well_types, [1960, 2017])
    g = dff[["API_WellNo", "Date_Well_Completed"]]
    g.index = g["Date_Well_Completed"]
    g = g.resample("A").count()

    colors = []
    for i in range(1960, 2018):
        if i >= int(year_slider[0]) and i < int(year_slider[1]):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")

    data = [
        dict(
            type="scatter",
            mode="markers",
            x=g.index,
            y=g["API_WellNo"] / 2,
            name="All Wells",
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="bar",
            x=g.index,
            y=g["API_WellNo"],
            name="All Wells",
            marker=dict(color=colors),
        ),
    ]

    layout_count["title"] = "Completed Wells/Year"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True

    figure = dict(data=data, layout=layout_count)
    return figure

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
    # print(province, flush=True)
    # print(Location, flush=True)
    #m=folium.Map([lat[0],lon[0]], zoom_start=4).add_to(f)   
    m=folium.Map(location=[lat, long], zoom_start=13).add_to(f)
    bar = vincent.Bar(alabama_data['Total'], height=100, width=200)
    data = json.loads(bar.to_json())
    v = features.Vega(data, width="100%", height="100%")
   
    for i , r in Location.iterrows():
        # print(r, flush=True)
        # print(r["Province"],flush=True)
        # print(province, flush=True)
        html = '''<h6>Gas Station</h6><br>Name:'''+r.loc["LocationName"]+'''<br>Postal Code:'''+r.loc["PostalCode"]
        iframe = folium.IFrame(html,
                       width=200,
                       height=100)
        popup = folium.Popup(iframe,
                     max_width=200)
        # popup = folium.Popup("Hello")
        
        if r["Province"] in province:

            if hr[0] <= r["RunOut"] <=hr[1]:
#                 print(r, flush=True)
                popup.add_child(v)
                folium.Marker(location=[r["Latitude"], r["Longitude"]], popup=popup, tooltip=tooltip, icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
                
            else:
                popup.add_child(v)
                folium.Marker(location=[r["Latitude"], r["Longitude"]], popup=popup, tooltip=tooltip, icon=folium.Icon(color="green", icon="info-sign")).add_to(m)
                
    
    #Save the map in a .html file
    sw = Location[['Latitude', 'Longitude']].min().values.tolist()
    ne = Location[['Latitude', 'Longitude']].max().values.tolist()
    m.fit_bounds([sw, ne]) 
    m.save("mymapnew.html")
    return open('mymapnew.html', 'r').read()

@app.callback(
              Output(component_id='route-map', component_property='srcDoc'),
              Input(component_id='hour_slider', component_property='value'),
              Input(component_id='province', component_property='value'),
)
def generate_route_map(hr, province):
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

if __name__ == '__main__':
    app.run_server(debug=True,port=8080, host="0.0.0.0")

