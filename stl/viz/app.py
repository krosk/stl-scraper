# import libraries
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np


# --------------------------------- Callbacks -------------------------------- #

# add callbacks to the map - filter data

# Output is not defined yet


def map_callback(app, dataframe, layout):

    @app.callback(
        Output("map-graph", "figure"),
        [
            Input("avg_rating-slider", "value"),
            Input("total_price-slider", "value"),
            Input("person_capacity-slider", "value"),
            Input("rating_accuracy-slider", "value"),
            Input("rating_checkin-slider", "value"),
            Input("rating_cleanliness-slider", "value"),
            Input("rating_communication-slider", "value"),
            Input("rating_location-slider", "value"),
            Input("rating_value-slider", "value"),
            Input("review_count-slider", "value"),
        ],
    )
    def update_graph(
        avg_rating_value,
        total_price_value,
        person_capacity_value,
        rating_accuracy_value,
        rating_checkin_value,
        rating_cleanliness_value,
        rating_communication_value,
        rating_location_value,
        rating_value_value,
        review_count_value,
        *args
    ):

        # Filter the data -> dynamic number of filters, based on the input
        filtered_df = dataframe[
            (dataframe["avg_rating"] >= avg_rating_value[0])
            & (dataframe["avg_rating"] <= avg_rating_value[1])
            & (dataframe["total_price"] >= total_price_value[0])
            & (dataframe["total_price"] <= total_price_value[1])
            & (dataframe["person_capacity"] >= person_capacity_value[0])
            & (dataframe["person_capacity"] <= person_capacity_value[1])
            & (dataframe["rating_accuracy"] >= rating_accuracy_value[0])
            & (dataframe["rating_accuracy"] <= rating_accuracy_value[1])
            & (dataframe["rating_checkin"] >= rating_checkin_value[0])
            & (dataframe["rating_checkin"] <= rating_checkin_value[1])
            & (dataframe["rating_cleanliness"] >= rating_cleanliness_value[0])
            & (dataframe["rating_cleanliness"] <= rating_cleanliness_value[1])
            & (dataframe["rating_communication"] >= rating_communication_value[0])
            & (dataframe["rating_communication"] <= rating_communication_value[1])
            & (dataframe["rating_location"] >= rating_location_value[0])
            & (dataframe["rating_location"] <= rating_location_value[1])
            & (dataframe["rating_value"] >= rating_value_value[0])
            & (dataframe["rating_value"] <= rating_value_value[1])
            & (dataframe["review_count"] >= review_count_value[0])
            & (dataframe["review_count"] <= review_count_value[1])
        ]

        # Create a hovertemplate string
        hovertemplate = map.create_template()

        # Create a scattermapbox trace
        trace = go.Scattermapbox(
            lat=filtered_df["latitude"],  # Latitude values for each data point
            # Longitude values for each data point
            lon=filtered_df["longitude"],
            mode="markers",
            marker=dict(
                # Adjust the size range based on standardized 'total_price' values
                size=14 + 2.5 * filtered_df["standardized_review_count"],
                # 'total_price' column values for each data point
                color=filtered_df["total_price"],
                colorscale="Viridis",  # You can choose any color scale you prefer
                # Add a colorbar with a title
                colorbar=dict(title="Total Price"),
                # Set opacity based on 'avg_rating' values
                opacity=filtered_df["avg_rating"] / \
                filtered_df["avg_rating"].max(),
                # Set the minimum value for color scale normalization
                cmin=filtered_df["total_price"].min(),
                # Set the maximum value for color scale normalization
                cmax=filtered_df["total_price"].max(),
                colorbar_ticksuffix=" zł",  # Add a prefix for colorbar tick values
                colorbar_tickformat=".2f",  # Set the format for colorbar tick values
            ),

            text=filtered_df["name"],  # Text labels for each data point
            customdata=np.array([
                filtered_df["person_capacity"],
                filtered_df["review_count"],
                filtered_df["rating_checkin"],
                filtered_df["rating_cleanliness"],
                filtered_df["rating_communication"],
                filtered_df["rating_location"],
                filtered_df["rating_value"],
                filtered_df["photo_count"],
            ]).T,

            hovertemplate=hovertemplate,
        )

        fig = go.Figure(data=[trace], layout=layout)

        # Return the figure
        return fig
