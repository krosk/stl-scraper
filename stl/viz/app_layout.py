# import libraries

# dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


# -------------------------------- App layout -------------------------------- #

class AppLayout:

    def __init__(self, fig, range_sliders):
        self.fig = fig
        self.range_sliders = range_sliders

    

    

    # app layout
    app.layout = dbc.Container(
        [

            # Title and description
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1("Airbnb Listings in Wroclaw, Poland"),
                            html.P(
                                """This dashboard shows the Airbnb listings in Wroclaw, Poland. \n
                                You can use the sliders to filter the listings based on their price, ratings, and other attributes."""
                            ),
                        ],
                        md=12,
                        # style={"margin-all": "30px"},
                    )
                ]
            ),

            # Filters and map
            dbc.Row(
                [
                    # Filters
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Filters"),
                                    dbc.CardBody(
                                        [
                                            html.Div(
                                                [slider.create_card_slider()
                                                for slider in range_sliders]
                                            )
                                        ]
                                    ),
                                ],
                                # style={"margin": "25px"},
                            )
                        ],
                        md=3,
                    ),

                    # Map
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Map"),
                                    # map that fits inside the card
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="map-graph",
                                                figure=fig,
                                                config={"scrollZoom": True},
                                                # scale map to fit the card body
                                                style={
                                                    "height": "100%", "width": "100%", "display": "block"},
                                            )
                                        ]
                                    ),
                                ],
                                style={"height": "100%"},
                            )
                        ],
                        md=9,
                    ),
                ],
                style={"margin-all": "30px"},
            ),
        ]
    )
