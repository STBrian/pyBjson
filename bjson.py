import json, math, os
from .utils import *
from pathlib import Path
from .bjsontojson_legacy import convertBjsonToJson_legacy
from .jsontobjson_legacy import convertJsonToBjson_legacy

debug_messages = False

def enableDebugMessages():
    global debug_messages
    debug_messages = True

def disableDebugMessages():
    global debug_messages
    debug_messages = False

def convertBjsonToJson(fp: str|Path):
    #print("[Warning] 'convertBjsonToJson' function is deprecated and will be removed in future versions")
    return convertBjsonToJson_legacy(fp)

def convertJsonToBjson(fp: str) -> (tuple[bool, int]):
    #print("[Warning] 'convertJsonToBjson' function is deprecated and will be removed in future versions")
    return convertJsonToBjson_legacy(fp)

class BJSONHashDatabase():
    def __init__(self, fp: str|Path|None = None):
        if fp != None:
            if type(fp) == str or type(fp) == Path:
                if type(fp) == str:
                    self.fp = Path(fp)
                else:
                    self.fp = fp

                if os.path.exists(self.fp):
                    with open(self.fp, "r", encoding="utf-8") as f:
                        self.json_data = json.loads(f.read())
                else:
                    raise FileNotFoundError()
            else:
                raise TypeError("'fp' must be str or Path type")
        else:
            self.json_data = None
            
    def open(self, fp: str|Path|None):
        if type(fp) == str or type(fp) == Path:
            if type(fp) == str:
                self.fp = Path(fp)
            else:
                self.fp = fp

            if os.path.exists(self.fp):
                with open(self.fp, "r", encoding="utf-8") as f:
                    self.json_data = json.loads(f.read())
            else:
                raise FileNotFoundError()
        else:
            raise TypeError("'fp' must be str or Path type")
            
    def save(self):
        with open(self.fp, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.json_data, indent=4))

    def addHashToDatabase(self, text: str, hash: bytes | list) -> None:
        if type(hash) == bytes:
            self.json_data[text] = list(hash)
        elif type(hash) == list:
            self.json_data[text] = hash
        else:
            raise TypeError("'hash' must be bytes or list")

    def getHash(self, key: str) -> (bytes | None):
        if self.json_data != None:
            if key in self.json_data:
                if type(self.json_data[key]) == list:
                    return bytes(self.json_data[key])
                else:
                    raise Exception(f"Unexpected hash type in database for {key}")
            else:
                return None

def getHeaders(data: bytes, hash_database: BJSONHashDatabase):
    global debug_messages

    text_region_start = (int.from_bytes(extract_chunk(data, 0), "little", signed=False) * 3 * 4) + 4
    text_region_lenght = int.from_bytes(extract_chunk(data, 0, 4, text_region_start), "little", signed=False)

    no_headers_region_start = text_region_start + text_region_lenght + 4
    no_headers_region_lenght = int.from_bytes(extract_chunk(data, 0, 4, no_headers_region_start), "little", signed=False)

    headers_region_start = no_headers_region_start + (no_headers_region_lenght * 4) + 4
    headers_region_lenght = int.from_bytes(extract_chunk(data, 0, 4, headers_region_start), "little", signed=False)

    headers_text_region_start = headers_region_start + (headers_region_lenght * 3 * 4) + 4
    headers = [""] * (headers_region_lenght + no_headers_region_lenght)

    for i in range(no_headers_region_lenght):
        no_header_idx = int.from_bytes(extract_chunk(data, i + 1, 4, no_headers_region_start), "little", signed=False)
        headers[no_header_idx - 1] = None
        
    for i in range(headers_region_lenght):
        hash = extract_chunk(data, i + 1, 4, headers_region_start)

        header_text_start = headers_text_region_start + int.from_bytes(extract_chunk(data, i + 2, 4, headers_region_start), "little", signed=False)
        header_text_end = headers_text_region_start + header_text_start
        while data[header_text_end] != 0:
            header_text_end += 1

        header_text_raw = data[header_text_start:header_text_end]
        header_text_decode = header_text_raw.decode('utf-8')

        header_idx = int.from_bytes(extract_chunk(data, i + 3, 4, headers_region_start), "little", signed=False)
        headers[header_idx - 1] = header_text_decode
        hash_database.addHashToDatabase(header_text_decode, hash)

        if debug_messages:
            print(extract_chunk(data, i + 1, 4, headers_region_start).hex(), extract_chunk(data, i + 2, 4, headers_region_start).hex(), extract_chunk(data, i + 3, 4, headers_region_start).hex(), header_text_decode)

    return headers

class BJSONEntry:
    def __init__(self):
        pass

class BJSON:
    def __init__(self):
        pass

    def open(self, fp: str|Path):
        global debug_messages

        if type(fp) == str:
            filepath = Path(fp)
        elif type(fp) == Path:
            filepath = fp
        else:
            raise ValueError()
        
        with open(filepath, "rb") as f:
            file_bytes = f.read()

        content_struct = None
        hash_db = BJSONHashDatabase()

        if debug_messages:
            print("[Info] Getting BJSON headers")

        headers = getHeaders(file_bytes, hash_db)
        text_region_start = (int.from_bytes(extract_chunk(file_bytes, 0), "little", signed=False) * 3 * 4) + 4
