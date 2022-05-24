
# Import required libraries
from dash import Dash, dcc, html, Input, Output, State, ClientsideFunction

# Multi-dropdown options
from controls import PROVINCE, PRODUCT_TYPES

# Create controls
province_options = [
    {"label": str(PROVINCE[province]), "value": str(province)}
    for province in PROVINCE
]

product_type_options = [
    {"label": str(PRODUCT_TYPES[product_type]), "value": str(product_type)}
    for product_type in PRODUCT_TYPES
]


station = html.Div(
    [
        # dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
       
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
                    className="pretty_container three columns",
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
                        ),


                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
       
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)