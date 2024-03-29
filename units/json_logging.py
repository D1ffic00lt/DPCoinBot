# -*- coding: utf-8 -*-
import _io
import json
import os

from typing import Union


class Json(object):
    __slots__ = (
        "file", "filename"
    )

    def __init__(self, filename: str) -> None:
        self.file: _io.TextIOWrapper
        self.filename: str = filename

    def json_load(self) -> Union[dict, list]:
        with open(f"{self.filename}", "r") as self.file:
            return json.load(self.file)

    def json_dump(self, data: Union[dict, list]) -> None:
        with open(f"{self.filename}", "w+") as self.file:
            json.dump(data, self.file)

    @staticmethod
    def get_ban_list() -> list:
        if not Json.check_file_exists(".json/ban_list.json"):
            return []
        return Json(".json/ban_list.json").json_load()

    @staticmethod
    def check_file_exists(filename: str) -> bool:
        if os.path.exists(f"{filename}"):
            return True
        return False
