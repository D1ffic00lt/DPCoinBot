# -*- coding: utf-8 -*-
from __future__ import annotations

import _io
import json
import os


class Json(object):
    def __init__(self, filename: str) -> None:
        self.file: _io.TextIOWrapper
        self.filename: str = filename

    def json_load(self) -> dict | list:
        with open(f".json/{self.filename}", "r") as self.file:
            return json.load(self.file)

    def json_dump(self, data: dict | list) -> None:
        with open(f".json/{self.filename}", "w+") as self.file:
            json.dump(data, self.file)

    @staticmethod
    def get_ban_list() -> list:
        return []

    @staticmethod
    def check_file_exists(filename: str) -> bool:
        if os.path.exists(f".json/{filename}"):
            return True
        return False
