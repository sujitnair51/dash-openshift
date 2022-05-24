import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
from dash_bootstrap_components._components.Container import Container
from content.station import station
from dash import Input, Output, State, ClientsideFunction, dcc, html
# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}



content = html.Div(id="page-content", style=CONTENT_STYLE)