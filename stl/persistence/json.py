import json
import os

from stl.persistence import PersistenceInterface

def load_json_dict(json_file):
    if os.path.isfile(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
    else:
        data = {}
    return data

def save_to_json(json_file, data_dict):
    with open(json_file, 'w') as f:
        json.dump(data_dict, f, indent=4, default=str)

def merge_dicts(dict1, dict2):
    merged = dict1.copy()
    for key, value in dict2.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged

def update_listing(listing_dict: dict, listing_list: list) -> dict:
    for listing in listing_list:
        id = listing['id']
        if id in listing_dict:
            # Merge existing entry with new information
            listing_dict[id] = merge_dicts(listing_dict[id], listing)
        else:
            # Add new entry to the dictionary
            listing_dict[id] = listing
    return listing_dict


class Json(PersistenceInterface):
    def __init__(self, json_path: str):
        self.__json_path = os.path.join(json_path, 'static', 'data.json')

    def save(self, query: str, listings: list):
        listing_dict = load_json_dict(self.__json_path)
        listing_dict = update_listing(listing_dict, listings)
        save_to_json(self.__json_path, listing_dict)
