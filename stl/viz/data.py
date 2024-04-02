

# Data manipulation file


# imports
from sklearn.preprocessing import StandardScaler
import pandas as pd

# dplyr
from dfply import *

# automatic report
from pandas_profiling import ProfileReport

# pprint - better formatting of data
from pprint import pprint

# numpy - for math
from numpy import mean, std, absolute

# standardize values in a column - scikit-learn
from sklearn.preprocessing import StandardScaler, MinMaxScaler


# LOAD DATA from csv #temporarily
df = pd.read_csv(
    '/home/gr00stl/Nextcloud/Projects/Python/Scraping/airbnb3/Wroclaw, Poland.csv'
)

# remove null columns
df = df.dropna(axis=1, how='all')


# # Subset data using dpfly
# - Check unique values for possible categorical variables

# # # Example masks

# # room_type = Private room
# private_room = df >> mask(X.room_type == 'Private room')

# # room_type = Entire home/apt
# entire_home = df >> mask(X.room_type == 'Entire home/apt')

# # review_count > 0
# with_reviews = df >> mask(X.review_count > 0)
# # # Note the need to replace NaN values with 0
# with_reviews = with_reviews.replace(np.nan, 0)
# # review_count = 0
# no_reviews = df >> mask(X.review_count == 0)

# # save few filters as list
# # # important columns - ['person_capacity', 'photo_count', price_rate	rating_accuracy	rating_checkin	rating_cleanliness	rating_communication	rating_location	rating_value	review_count...] -> check df.info()
# filters = [private_room, entire_home, no_reviews, with_reviews]


# Reasoning for standardization
# - Standardization is a common requirement for machine learning tasks.
# - Let's you compare scores between different types of variables.

# Find boolean columns
# # # boolean columns - print if == True
# print(df.columns[df.dtypes == bool])


class DataStandardizer:
    def __init__(self, df, select_rating=True):
        self.scaler = MinMaxScaler()

        # define self df
        self.df = df

        self.select_rating = select_rating

        # run selector
        self.selector()

    def selector(self):
        return self.select_rating_columns() if self.select_rating else self.select_numeric_columns()

    def select_numeric_columns(self):

        # select numeric columns
        self.df = self.df.select_dtypes(include=['int64', 'float64'])

        # Filter out columns with 'id' in the name
        self.df = self.df.loc[:, ~self.df.columns.str.contains('id')]

        # Filter out 'latitude' and 'longitude' columns
        self.df = self.df.loc[:, ~self.df.columns.str.contains(
            'latitude|longitude')]

        return self

    def select_rating_columns(self):
        # select rating columns
        self.df = self.df.loc[:, self.df.columns.str.contains('rating')]

        return self

    def standardize(self):
        # standardize
        self.df = pd.DataFrame(self.scaler.fit_transform(
            self.df), columns=self.df.columns, index=self.df.index)

        return self.df


# clean data

# # remove columns with one unique value
def remove_non_unique_columns(df):
    # remove columns with one unique value
    return df.loc[:, df.nunique() != 1]
