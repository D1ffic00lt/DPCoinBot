import json


class Json:
    def __init__(self, filename: str):
        self.file = None
        self.filename = filename

    def json_load(self):
        with open(f".json/{self.filename}", "r") as self.file:
            return json.load(self.file)

    def create_json(self, data: str):
        with open(f".json/{self.filename}", "w+") as self.file:
            self.file.write(data)

    def json_dump(self, data: dict or list):
        with open(f".json/{self.filename}", "w+") as self.file:
            json.dump(data, self.file)
