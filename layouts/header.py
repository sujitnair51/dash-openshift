import dash_bootstrap_components as dbc
from dash import html
from dash_bootstrap_components._components.Container import Container


PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

HEADER_STYLE = {
   "position": "fixed",
    "top": "0",
    "left": "0",
    "right": "0",
    "textDecoration": "none"
}

navbar =  html.Header(
  className='max-header',
  children=[

        dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                                dbc.Col(dbc.NavbarBrand("Navbar", className="ms-2")),
                            ],
                            align="left",
                            className="g-0",
                        ),
                        href="https://plotly.com",
                        style={"textDecoration": "none"},
                    ),
                   
                ]
            ),
            color="dark",
            dark=True,
            style=HEADER_STYLE,
        )
  ]
)