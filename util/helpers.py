"""
    Helper functions for loading and storing data, IO parsing etc.
"""


import json
import datetime


class DateTimeEncoder(json.JSONEncoder):
    """
        Datetime encoder for json objects
    """
    def default(self, o):
        """
            check if the json instance is a datetime object
            if so return the string value otherwise return
            the json instance
        """
        if isinstance(o, datetime.datetime):
            return str(o)
        return super().default(o)

def save_json(name, data):
    """
        Simple function to save a python dict as json file
    """
    with open(name, "w", encoding="utf-8") as json_file:
        json.dump(data , json_file, cls=DateTimeEncoder)

def load_json(name):
    """
        Simple function to load a json file as python dict
    """
    with open(name, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data
