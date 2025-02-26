# Copyright (C) 2025 STBrian
# This file is part of 'pyBjson' and is licensed under the GPLv3.
# See <https://www.gnu.org/licenses/> for details.

from pathlib import Path
import json, os

class MyDatabase():
    def __init__(self, fp):
        self.filepath = Path(fp)
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.json_data = json.loads(f.read())
        else:
            self.json_data = {}

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.json_data, indent=4))

    def addToDatabase(self, text: str, hashval: int) -> None:
        self.json_data[text] = hashval

    def getValue(self, key: str) -> int:
        if key in self.json_data:
            return self.json_data[key]
        else:
            return False
