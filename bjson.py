import io
import json
import struct
from pathlib import Path
from typing import BinaryIO
from dataclasses import dataclass

try:
    from .updateDatabase import MyDatabase
except:
    from updateDatabase import MyDatabase

class StructureError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class StructEntry:
    def __init__(self):
        pass

    def parseElement(self, file: BinaryIO):
        self.data_type = int.from_bytes(file.read(4), "little")
        raw_data1 = file.read(4)
        raw_data2 = file.read(4)
        if len(raw_data1) == 0 or len(raw_data2) == 0:
            raise ValueError("Unexpected empty value while reading structure")
        match self.data_type:
            case 0:
                # null value
                self.value1 = None
                self.value2 = 0
            case 1:
                # boolean value
                raw_data1 = int.from_bytes(raw_data1, "little")
                if raw_data1 == 1:
                    self.value1 = True
                else:
                    self.value1 = False
                self.value2 = 0
            case 2:
                # integer value
                self.value1 = int.from_bytes(raw_data1, "little", signed=True)
                self.value2 = 0
            case 3:
                # float value
                self.value1 = float("{:.5f}".format(struct.unpack('<f', raw_data1)[0]))
                self.value2 = 0
            case 4:
                # array type
                self.value1 = int.from_bytes(raw_data1, "little")
                self.value2 = int.from_bytes(raw_data2, "little")
            case 5:
                # array type
                self.value1 = int.from_bytes(raw_data1, "little")
                self.value2 = int.from_bytes(raw_data2, "little")
            case 6:
                # array type
                self.value1 = int.from_bytes(raw_data1, "little")
                self.value2 = int.from_bytes(raw_data2, "little")

@dataclass
class BJSONRegions:
    structre: list
    joinedStrings: bytes
    arrayIndexes: list
    headerIndexes: list
    joinedHeaderStrings: bytes

@dataclass
class Tracking:
    item_idx: int
    db: MyDatabase

class HeaderEntry:
    def __init__(self):
        pass

    def parseHeader(self, file: BinaryIO):
        self.stringHash = int.from_bytes(file.read(4), "little")
        self.stringPosition = int.from_bytes(file.read(4), "little")
        self.headerIndex = int.from_bytes(file.read(4), "little")

        if self.headerIndex <= 0:
            raise StructureError(f"Unexpected header index found at: {file.tell()}")

try:
    from .bjsonToJson import *
except:
    from bjsonToJson import *

class BJSONFile:
    def open(self, path: str | Path):
        if isinstance(path, str):
            path = Path(path)
        elif not isinstance(path, Path):
            raise TypeError("path expected to be 'str' or 'Path'")
        
        if not path.exists():
            raise Exception("path doesn't exists")
        else:
            with open(path, "rb") as f:
                self.data = io.BytesIO(f.read())
        return self

    def load(self, data: bytes | bytearray):
        if isinstance(data, bytes) or isinstance(data, bytearray):
            self.data = io.BytesIO(data)
        else:
            raise TypeError("data expected to be 'bytes' or 'bytearray'")
        return self

    def toJson(self, showDebug: bool = False):
        if showDebug:
            print("Getting structure")
        total_elements = int.from_bytes(self.data.read(4), "little")
        structEntries = []
        for i in range(total_elements):
            entry = StructEntry()
            entry.parseElement(self.data)
            structEntries.append(entry)

        if showDebug:
            print("Getting strings")
        lenght_strings = int.from_bytes(self.data.read(4), "little")
        joinedStrings = self.data.read(lenght_strings)
        
        if showDebug:
            print("Getting index for array items")
        total_array_items = int.from_bytes(self.data.read(4), "little")
        arrayIndexes = []
        for i in range(total_array_items):
            arrayIndexes.append(int.from_bytes(self.data.read(4), "little"))
            if arrayIndexes[-1] <= 0:
                raise StructureError(f"Unexpected array index found at: {self.data.tell()}")

        if showDebug:
            print("Getting index for headers")
        total_header_items = int.from_bytes(self.data.read(4), "little")
        headerIndexes = []
        for i in range(total_header_items):
            headerEntry = HeaderEntry()
            headerEntry.parseHeader(self.data)
            headerIndexes.append(headerEntry)

        if showDebug:
            print("Getting strings for headers")
        lenght_headers_strings = int.from_bytes(self.data.read(4), "little")
        joinedHeadersStrings = self.data.read(lenght_headers_strings)

        if showDebug:
            print("Assembling structure")
        track = Tracking(0, MyDatabase("./hash_database.json"))
        bjsonRegions = BJSONRegions(structEntries, joinedStrings, arrayIndexes, headerIndexes, joinedHeadersStrings)
        entry: StructEntry = bjsonRegions.structre.pop(0)
        if entry.data_type == 6:
            root = {}
            parseObject(root, entry, bjsonRegions, track)
        elif entry.data_type == 4:
            root = []
            parseArray(root, entry, bjsonRegions, track)
        else:
            raise StructureError(f"Data type {entry.data_type} is unknown or shouldn't go first in file. Expected 6 (object) or 4 (array)")

        return json.dumps(root, ensure_ascii=False, indent=4)