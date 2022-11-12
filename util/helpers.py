import json
import datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime.datetime):
            return (str(z))
        else:
            return super().default(z)

def save_json(name, data):
    with open(name, "w") as fp:
        json.dump(data , fp, cls=DateTimeEncoder)

def load_json(name):
    with open(name, "r") as fp:
        data = json.load(fp)
    return data
