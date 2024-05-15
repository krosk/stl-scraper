from stl.persistence.json import *
import pytest

@pytest.fixture
def sample_dict():
    return {1: {'id': 1, 'name': 'Listing 1', 'price': 100}, 2: {'id': 2, 'name': 'Listing 2', 'price': 200}}

@pytest.fixture
def sample_list():
    return [{'id': 1, 'price': 150}, {'id': 3, 'name': 'New Listing'}]

def test_update_data(sample_dict, sample_list):
    updated_dict = update_listing(sample_dict, sample_list)
    assert updated_dict == {1: {'id': 1, 'name': 'Listing 1', 'price': 150}, 2: {'id': 2, 'name': 'Listing 2', 'price': 200}, 3: {'id': 3, 'name': 'New Listing'}}

@pytest.fixture
def nested_listings():
    return [
        {'id': 1, 'name': 'apple', 'details': {'color': 'red', 'type': 'fruit'}},
        {'id': 2, 'name': 'banana', 'details': {'color': 'yellow', 'type': 'fruit'}}
    ]

def test_update_listing_nested_dictionaries(nested_listings):
    listing_dict = {1: {'id': 1, 'name': 'apple', 'details': {'color': 'green', 'type': 'fruit'}}}
    updated_dict = update_listing(listing_dict, nested_listings)
    assert updated_dict == {1: {'id': 1, 'name': 'apple', 'details': {'color': 'red', 'type': 'fruit'}}, 2: {'id': 2, 'name': 'banana', 'details': {'color': 'yellow', 'type': 'fruit'}}}

