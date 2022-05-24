# Import required libraries
from dash import dcc, html

trip =  html.Div(
    [
        # dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        # html.Div(id="output-clientside"),
       
        
        html.Div(
            [dcc.Loading(
                id="loading-map2",
                children=[html.Iframe(id='route-map', style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"})], type='circle')],

            id="countGraphContainer2",
            className="pretty_container",
         ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)