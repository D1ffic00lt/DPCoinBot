from __future__ import annotations

import _io
import json


class Json(object):
    def __init__(self, filename: str) -> None:
        self.file: _io.TextIOWrapper
        self.filename: str = filename

    def json_load(self) -> dict | list:
        with open(f".json/{self.filename}", "r") as self.file:
            return json.load(self.file)

    def create_json(self, data: str) -> None:
        with open(f".json/{self.filename}", "w+") as self.file:
            self.file.write(data)

    def json_dump(self, data: dict | list) -> None:
        with open(f".json/{self.filename}", "w+") as self.file:
            json.dump(data, self.file)

    def __repr__(self):
        return f"Json({self.filename})"
    