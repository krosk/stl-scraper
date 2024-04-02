# file for map vizualization in plotly graph objects - mapbox


# import libraries
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

# environmental variables
import os
# import your own map box token using dotenv
from dotenv import load_dotenv
load_dotenv()

mapbox_access_token = os.getenv('MAPBOX_TOKEN')


# -------------------------------- Map traces -------------------------------- #

def create_map_trace(
        df,
        hovertemplate,
        # suffix is taken from ENV variable

):

    return go.Scattermapbox(
        lat=df['latitude'],  # Latitude values for each data point
        lon=df['longitude'],  # Longitude values for each data point
        mode='markers',
        marker=dict(
            # Adjust the size range based on standardized 'total_price' values
            size=14 + 2.5 * df['standardized_review_count'], # ! change to different column as its not standardized
            # 'total_price' column values for each data point
            color=df['total_price'],
            colorscale='Viridis',  # You can choose any color scale you prefer
            colorbar=dict(title='Total Price'),  # Add a colorbar with a title
            # Set opacity based on 'avg_rating' values
            opacity=df['avg_rating'] / df['avg_rating'].max(),
            # Set the minimum value for color scale normalization
            cmin=df['total_price'].min(),
            # Set the maximum value for color scale normalization
            cmax=df['total_price'].max(),
            colorbar_ticksuffix=' zł',  # ! Add a prefix for colorbar tick values -> change to env variable
            colorbar_tickformat='.2f',  # Set the format for colorbar tick values
        ),
        text=df['name'],  # Text labels for each data point
        customdata=np.array(
            [
                df['person_capacity'],
                df['review_count'],
                df['rating_checkin'],
                df['rating_cleanliness'],
                df['rating_communication'],
                df['rating_location'],
                df['rating_value'],
                df['photo_count'],
            ]
        ).T,
        hovertemplate=hovertemplate,
    )


def create_template():
    hovertemplate = (
        "<b>Name</b>: %{text}<br>"
        "<b>Price</b>: %{marker.color:.2f}<br>"
        "<b>Person capacity</b>: %{customdata[0]}<br>"
        "<b>Ratings</b>:<br>"
        "- Count: %{customdata[1]}<br>"
        "- Checkin: %{customdata[2]:.2f}<br>"
        "- Cleanliness: %{customdata[3]:.2f}<br>"
        "- Communication: %{customdata[4]:.2f}<br>"
        "- Location: %{customdata[5]:.2f}<br>"
        "- Value: %{customdata[6]:.2f}<br>"
        "<b>No. of photos</b>: %{customdata[7]}<br>"
        "<extra></extra>"
    )

    return hovertemplate


class Section:

    # section for hovertemplate -> <h2> or <h3> or <h4> or <h5> or <h6>
    def __init__(self, section_name, section_hierarchy=2):
        self.section_name = section_name
        self.section_hierarchy = section_hierarchy

    def create_section(self):
        return f"<h{self.section_hierarchy}>{self.section_name}</h{self.section_hierarchy}><br>"    

class HoverTemplate:

    # i want user to create hovertemplate more easily, by passing relevant columns and choosing title or section for each column
    # hovertemplate should be passesd as a list of tuples, where each tuple is a (section, column, title)
    # section is a Section object, column is a string, title is a string
    def __init__(self, hovertemplate):
        self.hovertemplate = hovertemplate

    def create_hovertemplate(self):
        hovertemplate = ""

        # if section is empty string, then it will not be added to hovertemplate -> only Title: Value
        for section, column, title in self.hovertemplate:
            hovertemplate += section.create_section() if section.section_name != "" else ""
            hovertemplate += f"<b>{title}</b>: %{{{column}}}<br>"

        hovertemplate += "<extra></extra>"

        return hovertemplate
    
        



# -------------------------------- Map layout -------------------------------- #

def create_map_layout(
        center_lat,
        center_lon,
        zoom):

    return go.Layout(
        mapbox=dict(
            # Choose the map style (e.g., 'open-street-map', 'carto-positron', etc.)
            style='open-street-map',
            center=dict(
                # Use the mean latitude value for the map center
                lat=center_lat,
                # Use the mean longitude value for the map center
                lon=center_lon,
            ),
            zoom=zoom,  # Adjust the zoom level based on your data and preferences
        ),
    )


# create map
def create_map(
        trace,
        layout,
        height=800,
        width=800,
        margin=dict(
            # no margin
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
        bg_color="Ivory"):

    # Create the figure and add the trace to it
    fig = go.Figure(data=[trace], layout=layout)

    # set size to fit 2/3 column width ->
    fig.update_layout(
        autosize=False,
        width=width,
        height=height,
        margin=margin,
        # where to find plotly color names: https://www.w3schools.com/colors/colors_names.asp
        paper_bgcolor=bg_color,
    )

    # Show the figure
    fig.show()
