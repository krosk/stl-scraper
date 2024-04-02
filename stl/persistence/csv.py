import csv

from stl.persistence import PersistenceInterface


class Csv(PersistenceInterface):

    def __init__(self, csv_path: str):
        self.__csv_path = csv_path

    def save(self, query: str, listings: list):
        with open(self.__csv_path, 'w', encoding='utf-8', newline='') as csvfile:
            fieldnames = set().union(*[listing.keys() for listing in listings])
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(listings)
