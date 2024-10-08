import json, math, os
from .utils import *
from pathlib import Path
from .bjsontojson_legacy import convertBjsonToJson_legacy
from .jsontobjson_legacy import convertJsonToBjson_legacy

debug_messages = False

def enableBJSONDebugMessages():
    global debug_messages
    debug_messages = True

def disableBJSONDebugMessages():
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
            self.json_data = {}
            
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

def getBJSONHeaders(data: bytes, hash_database: BJSONHashDatabase):
    global debug_messages

    text_region_start = (int.from_bytes(extract_chunk(data, 0), "little", signed=False) * 3 * 4) + 4
    text_region_lenght = int.from_bytes(extract_chunk(data, 0, 4, text_region_start), "little", signed=False)

    no_headers_region_start = text_region_start + text_region_lenght + 4
    no_headers_region_lenght = int.from_bytes(extract_chunk(data, 0, 4, no_headers_region_start), "little", signed=False)
    if debug_messages:
        print(f"[Info] No Header Lenght: {no_headers_region_lenght}")

    headers_region_start = no_headers_region_start + (no_headers_region_lenght * 4) + 4
    headers_region_lenght = int.from_bytes(extract_chunk(data, 0, 4, headers_region_start), "little", signed=False)
    if debug_messages:
        print(f"[Info] Header Lenght: {headers_region_lenght}")

    headers_text_region_start = headers_region_start + (headers_region_lenght * 3 * 4) + 8
    headers = [""] * (headers_region_lenght + no_headers_region_lenght)

    for i in range(no_headers_region_lenght):
        no_header_idx = int.from_bytes(extract_chunk(data, i + 1, 4, no_headers_region_start), "little", signed=False)
        headers[no_header_idx - 1] = None
        
    for i in range(headers_region_lenght):
        idx = (i * 3) + 1
        hash = extract_chunk(data, idx, 4, headers_region_start)

        header_text_start = headers_text_region_start + int.from_bytes(extract_chunk(data, idx + 1, 4, headers_region_start), "little", signed=False)
        header_text_end = header_text_start
        while data[header_text_end] != 0:
            header_text_end += 1

        header_text_raw = data[header_text_start:header_text_end]
        header_text_decode = header_text_raw.decode('utf-8')

        header_idx = int.from_bytes(extract_chunk(data, idx + 2, 4, headers_region_start), "little", signed=False)
        headers[header_idx - 1] = header_text_decode
        hash_database.addHashToDatabase(header_text_decode, hash)

        if debug_messages:
            print("[Info]", extract_chunk(data, idx, 4, headers_region_start).hex(), extract_chunk(data, idx + 1, 4, headers_region_start).hex(), extract_chunk(data, idx + 2, 4, headers_region_start).hex(), header_text_decode)

    return headers

def getObject(object: dict | list, file_data, n_objects: int, headers, text_region_start) -> int:
    if type(object) == dict or type(object) == list:
        new_object = {}
        idx = n_objects * 3 + 1
        structure_lenght = int.from_bytes(extract_chunk(file_data, idx + 1), "little", signed=False)
        if type(object) == dict:
            new_object_header = headers[n_objects]
        n_objects += 1

        for i in range(structure_lenght):
            idx = n_objects * 3 + 1

            data_type = int.from_bytes(extract_chunk(file_data, idx), "little", signed=False)
            if data_type == 6:
                # JSON Object type
                n_objects = getObject(new_object, file_data, n_objects, headers, text_region_start)
            elif data_type == 5:
                # JSON String type
                n_objects = getString(new_object, file_data, n_objects, headers, text_region_start)
            elif data_type == 4:
                # JSON Array type
                pass

        if type(object) == dict:
            object[new_object_header] = new_object
        elif type(object) == list:
            object.append(new_object)
        else:
            raise TypeError("'object' must be dict or list")
    
        return n_objects
    else:
        raise TypeError("'object' must be dict or list")

def getString(object: dict | list, file_data: bytes, n_objects: int, headers: list, text_region_start: int) -> int:
    if type(object) == dict or type(object) == list:
        idx = n_objects * 3 + 1
        if type(object) == dict:
            object_header = headers[n_objects]
        n_objects += 1

        text_idx = int.from_bytes(extract_chunk(file_data, idx + 2), "little", signed=False)
        text_start = text_region_start + text_idx
        text_end = text_start
        while (file_data[text_end] != 0):
            text_end += 1

        text_raw = file_data[text_start:text_end]
        text_decode = text_raw.decode('utf-8')

        if type(object) == dict:
            object[object_header] = text_decode
        elif type(object) == list:
            object.append(text_decode)
        else:
            raise TypeError("'object' must be dict or list")
    
        return n_objects
    else:
        raise TypeError("'object' must be dict or list")

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

        headers = getBJSONHeaders(file_bytes, hash_db)
        n_structure_objects = int.from_bytes(extract_chunk(file_bytes, 0), "little", signed=False)
        text_region_start = (n_structure_objects * 3 * 4) + 8

        if debug_messages:
            print("[Info] Getting BJSON structure")

        data_type = int.from_bytes(extract_chunk(file_bytes, 1), "little", signed=False)
        if data_type == 6:
            # JSON Object type
            content_struct = {}
            structure_lenght = int.from_bytes(extract_chunk(file_bytes, 2), "little", signed=False)
        elif data_type == 4:
            # JSON Array type
            content_struct = []
            structure_lenght = int.from_bytes(extract_chunk(file_bytes, 2), "little", signed=False)
        else:
            raise Exception("Unexpected structure opening value")
        
        n_objects = 1
        for i in range(structure_lenght):
            idx = n_objects * 3 + 1

            data_type = int.from_bytes(extract_chunk(file_bytes, idx), "little", signed=False)
            if data_type == 6:
                # JSON Object type
                n_objects = getObject(content_struct, file_bytes, n_objects, headers, text_region_start)
            elif data_type == 5:
                # JSON String type
                n_objects = getString(content_struct, file_bytes, n_objects, headers, text_region_start)