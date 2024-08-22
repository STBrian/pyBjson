import json, math, sys
from .utils import *
from pathlib import Path
from .updateDatabase import MyDatabase

def addObject(sdata: list, tdata: list, nhdata: list, hdata: list, htdata: list, header: str | None, data: dict, obj_close: int = 0, list_close: int = 0, g_count = 0, hashdb: MyDatabase = None):
    tmp_nhdata = []
    last_close_nhdata = []
    tmp_hdata = []
    last_close_hdata = []
    self_hdata = []
    sdata.extend(int_to_bytes(6, "little"))
    sdata.extend(int_to_bytes(len(data), "little"))
    end_idx = len(sdata)
    local_count = g_count
    #sdata.extend([0] * 4)
    if header == None and local_count != 0:
        tmp_nhdata.extend(int_to_bytes(g_count, "little"))
    if header != None:
        if hashdb.getValue(header):
            self_hdata.extend(hashdb.getValue(header))
        else:
            print(f"Missing hash value for {header}")
            return 1
        self_hdata.extend(int_to_bytes(len(htdata) - 4, "little"))
        self_hdata.extend(int_to_bytes(g_count, "little"))
        htdata.extend(header.encode("utf-8"))
        htdata.append(0)
    g_count += 1
    for key in data:
        if type(data[key]) == bool:
            value = addBool(sdata, tmp_nhdata, tmp_hdata, htdata, key, data[key], g_count, hashdb=hashdb)
            if value != None:
                return value
        elif type(data[key]) == int:
            value = addInt(sdata, tmp_nhdata, tmp_hdata, htdata, key, data[key], g_count, hashdb=hashdb)
            if value != None:
                return value
        elif type(data[key]) == float:
            value = addFloat(sdata, tmp_nhdata, tmp_hdata, htdata, key, data[key], g_count, hashdb=hashdb)
            if value != None:
                return value
        elif type(data[key]) == list:
            value = addList(sdata, tdata, [], [], htdata, key, data[key], obj_close, list_close, g_count, hashdb=hashdb)
            if value == 1:
                return value
            else:
                obj_hdata, last_close_nhdata, last_close_hdata, g_count, obj_close, list_close = value
                nhdata.extend(last_close_nhdata)
                hdata.extend(last_close_hdata)
                tmp_hdata.extend(obj_hdata)
        elif type(data[key]) == str:
            value = addString(sdata, tdata, tmp_nhdata, tmp_hdata, htdata, key, data[key], g_count, hashdb=hashdb)
            if value != None:
                return value
        elif type(data[key]) == dict:
            value = addObject(sdata, tdata, [], [], htdata, key, data[key], obj_close, list_close, g_count, hashdb=hashdb)
            if value == 1:
                return value
            else:
                obj_hdata, last_close_nhdata, last_close_hdata, g_count, obj_close, list_close = value
                nhdata.extend(last_close_nhdata)
                hdata.extend(last_close_hdata)
                tmp_hdata.extend(obj_hdata)
        
        if type(data[key]) != dict and type(data[key]) != list:
            g_count += 1
    sdata[end_idx:4] = int_to_bytes(obj_close, "little")
    obj_count = len(data)
    nhdata.extend(tmp_nhdata)
    hdata.extend(tmp_hdata)
    return self_hdata, nhdata, hdata, g_count, obj_close + obj_count, list_close

def addList(sdata: list, tdata: list, nhdata: list, hdata: list, htdata: list, header: str | None, data: list, obj_close: int = 0, list_close: int = 0, g_count = 0, hashdb: MyDatabase = None):
    tmp_nhdata = []
    last_close_nhdata = []
    tmp_hdata = []
    last_close_hdata = []
    self_hdata = []
    sdata.extend(int_to_bytes(4, "little"))
    sdata.extend(int_to_bytes(len(data), "little"))
    end_idx = len(sdata)
    #sdata.extend([0] * 4)
    local_count = g_count
    if header == None and local_count != 0:
        tmp_nhdata.extend(int_to_bytes(g_count, "little"))
    if header != None:
        if hashdb.getValue(header):
            self_hdata.extend(hashdb.getValue(header))
        else:
            print(f"Missing hash value for {header}")
            return 1
        self_hdata.extend(int_to_bytes(len(htdata) - 4, "little"))
        self_hdata.extend(int_to_bytes(g_count, "little"))
        htdata.extend(header.encode("utf-8"))
        htdata.append(0)
    g_count += 1
    for key in data:
        if type(key) == bool:
            value = addBool(sdata, tmp_nhdata, tmp_hdata, htdata, None, key, g_count)
            if value != None:
                return value
        elif type(key) == int:
            value = addInt(sdata, tmp_nhdata, tmp_hdata, htdata, None, key, g_count)
            if value != None:
                return value
        elif type(key) == float:
            value = addFloat(sdata, tmp_nhdata, tmp_hdata, htdata, None, key, g_count)
            if value != None:
                return value
        elif type(key) == list:
            value = addList(sdata, tdata, [], [], htdata, None, key, obj_close, list_close, g_count, hashdb=hashdb)
            if value == 1:
                return value
            else:
                obj_hdata, last_close_nhdata, last_close_hdata, g_count, obj_close, list_close = value
                nhdata.extend(last_close_nhdata[:-4])
                tmp_nhdata.extend(last_close_nhdata[-4:])
                hdata.extend(last_close_hdata)
        elif type(key) == str:
            value = addString(sdata, tdata, tmp_nhdata, hdata, htdata, None, key, g_count, hashdb=hashdb)
            if value != None:
                return value
        elif type(key) == dict:
            value = addObject(sdata, tdata, [], [], htdata, None, key, obj_close, list_close, g_count, hashdb=hashdb)
            if value == 1:
                return value
            else:
                obj_hdata, last_close_nhdata, last_close_hdata, g_count, obj_close, list_close = value
                nhdata.extend(last_close_nhdata[:-4])
                tmp_nhdata.extend(last_close_nhdata[-4:])
                hdata.extend(last_close_hdata)

        if type(key) != dict and type(key) != list:
            g_count += 1
    sdata[end_idx:4] = int_to_bytes(list_close, "little")
    list_count = len(data)
    nhdata.extend(tmp_nhdata)
    hdata.extend(tmp_hdata)
    return self_hdata, nhdata, hdata, g_count, obj_close, list_close + list_count

def addBool(sdata: list, nhdata: list, hdata: list, htdata: list, header: str | None, value: bool, count: int, hashdb: MyDatabase = None):
    sdata.extend(int_to_bytes(1, "little"))
    sdata.extend(int_to_bytes(bool_to_int(value), "little"))
    sdata.extend(int_to_bytes(0, "little"))
    if header == None:
        nhdata.extend(int_to_bytes(count, "little"))
    if header != None:
        if hashdb.getValue(header):
            hdata.extend(hashdb.getValue(header))
        else:
            print(f"Missing hash value for {header}")
            return 1
        hdata.extend(int_to_bytes(len(htdata) - 4, "little"))
        hdata.extend(int_to_bytes(count, "little"))
        htdata.extend(header.encode("utf-8"))
        htdata.append(0)

def addInt(sdata: list, nhdata: list, hdata: list, htdata: list, header: str | None, value: int, count: int, hashdb: MyDatabase = None):
    sdata.extend(int_to_bytes(2, "little"))
    sdata.extend(int_to_bytes(value, "little"))
    sdata.extend(int_to_bytes(0, "little"))
    if header == None:
        nhdata.extend(int_to_bytes(count, "little"))
    if header != None:
        if hashdb.getValue(header):
            hdata.extend(hashdb.getValue(header))
        else:
            print(f"Missing hash value for {header}")
            return 1
        hdata.extend(int_to_bytes(len(htdata) - 4, "little"))
        hdata.extend(int_to_bytes(count, "little"))
        htdata.extend(header.encode("utf-8"))
        htdata.append(0)

def addFloat(sdata: list, nhdata: list, hdata: list, htdata: list, header: str | None, value: float, count: int, hashdb: MyDatabase = None):
    sdata.extend(int_to_bytes(3, "little"))
    sdata.extend(float_to_bytes(value, "little"))
    sdata.extend(int_to_bytes(0, "little"))
    if header == None:
        nhdata.extend(int_to_bytes(count, "little"))
    if header != None:
        if hashdb.getValue(header):
            hdata.extend(hashdb.getValue(header))
        else:
            print(f"Missing hash value for {header}")
            return 1
        hdata.extend(int_to_bytes(len(htdata) - 4, "little"))
        hdata.extend(int_to_bytes(count, "little"))
        htdata.extend(header.encode("utf-8"))
        htdata.append(0)

def addString(sdata: list, tdata: list, nhdata: list, hdata: list, htdata: list, header: str | None, value: str, count: int, hashdb: MyDatabase = None):
    sdata.extend(int_to_bytes(5, "little"))
    if hashdb.getValue(value):
        sdata.extend(hashdb.getValue(value))
    else:
        print(f"Missing hash value for {value}")
        return 1
    sdata.extend(int_to_bytes(len(tdata) - 4, "little"))
    tdata.extend(value.encode('utf-8'))
    tdata.append(0)
    if header == None:
        nhdata.extend(int_to_bytes(count, "little"))
    if header != None:
        if hashdb.getValue(header):
            hdata.extend(hashdb.getValue(header))
        else:
            print(f"Missing hash value for {header}")
            return 1
        hdata.extend(int_to_bytes(len(htdata) - 4, "little"))
        hdata.extend(int_to_bytes(count, "little"))
        htdata.extend(header.encode("utf-8"))
        htdata.append(0)

def convertJsonToBjson_legacy(fp: str) -> (tuple[bool, int]):
    hash_database = MyDatabase("hash_database.json")
    filepath = Path(fp)
    with open(filepath, "r", encoding='utf-8') as f:
        json_file = json.loads(f.read())
    
    structure_data = [0] * 4
    text_data = [0] * 4
    no_headers_data = [0] * 4
    headers_data = [0] * 4
    headers_text_data = [0] * 4

    if type(json_file) == dict:
        value = addObject(structure_data, text_data, no_headers_data, headers_data, headers_text_data, None, json_file, hashdb=hash_database)
        if value == 1:
            return False, value
    elif type(json_file) == list:
        value = addList(structure_data, text_data, no_headers_data, headers_data, headers_text_data, None, json_file, hashdb=hash_database)
        if value == 1:
            return False, value
    
    structure_data[0:4] = uint_to_bytes(math.floor((len(structure_data) - 4) / (3 * 4)), "little")
    text_data[0:4] = uint_to_bytes(len(text_data) - 4, "little")
    no_headers_data[0:4] = uint_to_bytes(math.floor((len(no_headers_data) - 4) / 4), "little")
    headers_data[0:4] = uint_to_bytes(math.floor((len(headers_data) - 4) / (3 * 4)), "little")
    headers_text_data[0:4] = uint_to_bytes(len(headers_text_data) - 4, "little")

    output_data = []
    output_data.extend(structure_data)
    output_data.extend(text_data)
    output_data.extend(no_headers_data)
    output_data.extend(headers_data)
    output_data.extend(headers_text_data)

    with open(f"{filepath.stem}_converted.bjson", "wb") as f:
        f.write(bytearray(output_data))

    return True, 0