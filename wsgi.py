# Import required libraries
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from layouts.header import navbar
from layouts.content import content as page_content
from layouts.sidebar import sidebar

app = dash.Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}], 
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = "DO Optimization"
server = app.server
application = app.server

app.layout = html.Div(
    [dcc.Location(id="url"), 
    navbar,
    sidebar, 
    page_content
    ]
)

import callback

if __name__ == '__main__':
    app.run_server(debug=True,port=8080, host="0.0.0.0")

