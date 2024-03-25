import json, math, sys
from conversions import *
from pathlib import Path
from JOAAThash import getLittleJOAAThash

def extract_chunk(data: bytes, idx: int, size: int = 4, start_from: int = 0):
    start = idx * size + start_from
    return data[start:start + size]

def getHeaders(data: bytes):
    text_region_start = (int.from_bytes(extract_chunk(data, 0), "little", signed=False) * 3 * 4) + 4
    lenght_text_r = int.from_bytes(extract_chunk(data, 0, 4, text_region_start), "little", signed=False)
    region_start = text_region_start + lenght_text_r + 4
    pre_region_len = int.from_bytes(extract_chunk(data, 0, 4, region_start), "little", signed=False)
    lenght = int.from_bytes(extract_chunk(data, pre_region_len + 1, 4, region_start), "little", signed=False)
    print(pre_region_len)
    print(lenght)
    headers = [""] * (lenght + pre_region_len)
    headers_text_start = region_start + (pre_region_len + 1) * 4 + (lenght) * 4 * 3 + 4
    for i in range(pre_region_len):
        idx = int.from_bytes(extract_chunk(data, i + 1, 4, region_start), "little", signed=False)
        headers[idx - 1] = None
    for i in range(lenght):
        idx = pre_region_len + 1 + i * 3 + 1
        headers_idx = int.from_bytes(extract_chunk(data, idx + 1, 4, region_start), "little", signed=False)
        headers_idx_end = headers_text_start + 4 + headers_idx
        while True:
            if data[headers_idx_end] == 0:
                break
            else:
                headers_idx_end += 1
        header_part = data[headers_text_start + 4 + headers_idx:headers_idx_end]
        header_idx = int.from_bytes(extract_chunk(data, idx + 2, 4, region_start), "little", signed=False) # Nota es distinto a headers_idx
        headers[header_idx - 1] = header_part.decode('utf-8')
    return headers

def convertBjsonToJson(fp: str):
    filepath = Path(fp)
    with open(filepath, "rb") as f:
        data_bytes = f.read()

    json_dict = None
    place_dir = []

    text_region_idx = int.from_bytes(extract_chunk(data_bytes, 0), "little", signed=False) * 3 + 1
    lenght_text_region = int.from_bytes(extract_chunk(data_bytes, text_region_idx), "little", signed=False)
    headers = getHeaders(data_bytes)
    print(headers)
    #sys.exit()

    for i in range(int.from_bytes(extract_chunk(data_bytes, 0), "little", signed=False)):
        idx = i * 3 + 1
        type_extracted = int.from_bytes(extract_chunk(data_bytes, idx), "little", signed=False)
        if type_extracted == 6:
            if json_dict == None:
                json_dict = {}
                tmp = []
                tmp.append(json_dict)
                tmp.append("array")
                tmp.append(int.from_bytes(extract_chunk(data_bytes, idx + 1), "little", signed=False))
                tmp.append(0)
                place_dir.append(tmp)
            else:
                tmp = place_dir[-1]
                dir = tmp[0]
                if tmp[1] == "array":
                    # Header
                    dir[f"{headers[i-1]}"] = {}
                    tmp2 = []
                    # Header in tmp
                    tmp2.append(dir[f"{headers[i-1]}"])
                    tmp2.append("array")
                    tmp2.append(int.from_bytes(extract_chunk(data_bytes, idx + 1), "little", signed=False))
                    tmp2.append(0)
                    place_dir.append(tmp2)
                elif tmp[1] == "list":
                    dir.append({})
                    tmp2 = []
                    tmp2.append(dir[-1])
                    tmp2.append("array")
                    tmp2.append(int.from_bytes(extract_chunk(data_bytes, idx + 1), "little", signed=False))
                    tmp2.append(0)
                    place_dir.append(tmp2)
                tmp[3] += 1
                if tmp[3] >= tmp[2]:
                    place_dir.pop(-2)
        elif type_extracted == 5:
            tmp = place_dir[-1]
            dir = tmp[0]
            if tmp[1] == "array":
                text_idx = int.from_bytes(extract_chunk(data_bytes, idx + 2), "little", signed=False)
                text_idx_end = ((text_region_idx + 1) * 4) + text_idx
                while True:
                    if data_bytes[text_idx_end] == 0:
                        break
                    else:
                        text_idx_end += 1
                text_part = data_bytes[((text_region_idx + 1) * 4) + text_idx:text_idx_end]
                # Header
                dir[f"{headers[i-1]}"] = text_part.decode("utf-8")
            elif tmp[1] == "list":
                text_idx = int.from_bytes(extract_chunk(data_bytes, idx + 2), "little", signed=False)
                text_idx_end = ((text_region_idx + 1) * 4) + text_idx
                while True:
                    if data_bytes[text_idx_end] == 0:
                        break
                    else:
                        text_idx_end += 1
                text_part = data_bytes[((text_region_idx + 1) * 4) + text_idx:text_idx_end]
                dir.append(text_part.decode("utf-8"))
            tmp[3] += 1
        elif type_extracted == 4:
            tmp = place_dir[-1]
            dir = tmp[0]
            # Header
            dir[f"{headers[i-1]}"] = []
            tmp2 = []
            # Header in tmp
            tmp2.append(dir[f"{headers[i-1]}"])
            tmp2.append("list")
            tmp2.append(int.from_bytes(extract_chunk(data_bytes, idx + 1), "little", signed=False))
            tmp2.append(0)
            place_dir.append(tmp2)
            tmp[3] += 1
            if tmp[3] >= tmp[2]:
                place_dir.pop(-2)
        elif type_extracted == 3:
            tmp = place_dir[-1]
            dir = tmp[0]
            if tmp[1] == "array":
                float_num = bytes_to_float(extract_chunk(data_bytes, idx + 1), "little")
                # Header
                dir[f"{headers[i-1]}"] = float("{:.2f}".format(float_num))
            elif tmp[1] == "list":
                float_num = bytes_to_float(extract_chunk(data_bytes, idx + 1), "little")
                dir.append(float("{:.2f}".format(float_num)))
            tmp[3] += 1
        elif type_extracted == 2:
            tmp = place_dir[-1]
            dir = tmp[0]
            if tmp[1] == "array":
                # Header
                dir[f"{headers[i-1]}"] = bytes_to_int(extract_chunk(data_bytes, idx + 1), "little")
            elif tmp[1] == "list":
                dir.append(bytes_to_int(extract_chunk(data_bytes, idx + 1), "little"))
            tmp[3] += 1
        elif type_extracted == 1:
            tmp = place_dir[-1]
            dir = tmp[0]
            if tmp[1] == "array":
                bool_num = int.from_bytes(extract_chunk(data_bytes, idx + 1), "little", signed=False)
                # With header
                if bool_num == 0:
                    dir[f"{headers[i-1]}"] = False
                elif bool_num == 1:
                    dir[f"{headers[i-1]}"] = True
            elif tmp[1] == "list":
                bool_num = int.from_bytes(extract_chunk(data_bytes, idx + 1), "little", signed=False)
                if bool_num == 0:
                    dir.append(False)
                elif bool_num == 1:
                    dir.append(True)
            tmp[3] += 1

        if len(place_dir) > 0:
            check = place_dir[-1]
            if check[3] >= check[2]:
                place_dir.pop(-1)

    json_string = json.dumps(json_dict, indent=4)
    print(json_dict)

    with open(f"{filepath.stem}_converted.json", "w", encoding='utf-8') as f:
        f.write(json_string)

def addObject(sdata: list, tdata: list, nhdata: list, hdata: list, htdata: list, header: str | None, data: dict, obj_close: int = 0, list_close: int = 0, g_count = 0):
    sdata.extend(int_to_bytes(6, "little"))
    sdata.extend(int_to_bytes(len(data), "little"))
    end_idx = len(sdata)
    #sdata.extend([0] * 4)
    if header == None and g_count != 0:
        nhdata.extend(int_to_bytes(g_count, "little"))
    if header != None:
        hdata.extend(getLittleJOAAThash(header))
        hdata.extend(int_to_bytes(len(htdata) - 4, "little"))
        hdata.extend(int_to_bytes(g_count, "little"))
        htdata.extend(header.encode("utf-8"))
        htdata.append(0)
    g_count += 1
    for key in data:
        if type(data[key]) == bool:
            addBool(sdata, nhdata, hdata, htdata, key, data[key], g_count)
        elif type(data[key]) == int:
            addInt(sdata, nhdata, hdata, htdata, key, data[key], g_count)
        elif type(data[key]) == float:
            addFloat(sdata, nhdata, hdata, htdata, key, data[key], g_count)
        elif type(data[key]) == list:
            g_count, obj_close, list_close = addList(sdata, tdata, nhdata, hdata, htdata, key, data[key], obj_close, list_close, g_count)
        elif type(data[key]) == str:
            addString(sdata, tdata, nhdata, hdata, htdata, key, data[key], g_count)
        elif type(data[key]) == dict:
            g_count, obj_close, list_close = addObject(sdata, tdata, nhdata, hdata, htdata, key, data[key], obj_close, list_close, g_count)
        
        if type(data[key]) != dict and type(data[key]) != list:
            g_count += 1
    sdata[end_idx:4] = int_to_bytes(obj_close, "little")
    obj_count = len(data)
    return g_count, obj_close + obj_count, list_close

def addList(sdata: list, tdata: list, nhdata: list, hdata: list, htdata: list, header: str | None, data: list, obj_close: int = 0, list_close: int = 0, g_count = 0):
    sdata.extend(int_to_bytes(4, "little"))
    sdata.extend(int_to_bytes(len(data), "little"))
    end_idx = len(sdata)
    #sdata.extend([0] * 4)
    if header == None and g_count != 0:
        nhdata.extend(int_to_bytes(g_count, "little"))
    if header != None:
        hdata.extend(getLittleJOAAThash(header))
        hdata.extend(int_to_bytes(len(htdata) - 4, "little"))
        hdata.extend(int_to_bytes(g_count, "little"))
        htdata.extend(header.encode("utf-8"))
        htdata.append(0)
    g_count += 1
    for key in data:
        if type(key) == bool:
            addBool(sdata, nhdata, hdata, htdata, None, key, g_count)
        elif type(key) == int:
            addInt(sdata, nhdata, hdata, htdata, None, key, g_count)
        elif type(key) == float:
            addFloat(sdata, nhdata, hdata, htdata, None, key, g_count)
        elif type(key) == list:
            g_count, obj_close, list_close = addList(sdata, tdata, nhdata, hdata, htdata, None, key, obj_close, list_close, g_count)
        elif type(key) == str:
            addString(sdata, tdata, nhdata, hdata, htdata, None, key, g_count)
        elif type(key) == dict:
            g_count, obj_close, list_close = addObject(sdata, tdata, nhdata, hdata, htdata, None, key, obj_close, list_close, g_count)
        
        if type(key) != dict and type(key) != list:
            g_count += 1
    sdata[end_idx:4] = int_to_bytes(list_close, "little")
    list_count = len(data)
    return g_count, obj_close, list_close + list_count

def addBool(sdata: list, nhdata: list, hdata: list, htdata: list, header: str | None, value: bool, count: int):
    sdata.extend(int_to_bytes(1, "little"))
    sdata.extend(int_to_bytes(bool_to_int(value), "little"))
    sdata.extend(int_to_bytes(0, "little"))
    if header == None:
        nhdata.extend(int_to_bytes(count, "little"))
    if header != None:
        hdata.extend(getLittleJOAAThash(header))
        hdata.extend(int_to_bytes(len(htdata) - 4, "little"))
        hdata.extend(int_to_bytes(count, "little"))
        htdata.extend(header.encode("utf-8"))
        htdata.append(0)

def addInt(sdata: list, nhdata: list, hdata: list, htdata: list, header: str | None, value: int, count: int):
    sdata.extend(int_to_bytes(2, "little"))
    sdata.extend(int_to_bytes(value, "little"))
    sdata.extend(int_to_bytes(0, "little"))
    if header == None:
        nhdata.extend(int_to_bytes(count, "little"))
    if header != None:
        hdata.extend(getLittleJOAAThash(header))
        hdata.extend(int_to_bytes(len(htdata) - 4, "little"))
        hdata.extend(int_to_bytes(count, "little"))
        htdata.extend(header.encode("utf-8"))
        htdata.append(0)

def addFloat(sdata: list, nhdata: list, hdata: list, htdata: list, header: str | None, value: float, count: int):
    sdata.extend(int_to_bytes(3, "little"))
    sdata.extend(float_to_bytes(value, "little"))
    sdata.extend(int_to_bytes(0, "little"))
    if header == None:
        nhdata.extend(int_to_bytes(count, "little"))
    if header != None:
        hdata.extend(getLittleJOAAThash(header))
        hdata.extend(int_to_bytes(len(htdata) - 4, "little"))
        hdata.extend(int_to_bytes(count, "little"))
        htdata.extend(header.encode("utf-8"))
        htdata.append(0)

def addString(sdata: list, tdata: list, nhdata: list, hdata: list, htdata: list, header: str | None, value: str, count: int):
    sdata.extend(int_to_bytes(5, "little"))
    sdata.extend(getLittleJOAAThash(value))
    sdata.extend(int_to_bytes(len(tdata) - 4, "little"))
    tdata.extend(value.encode('utf-8'))
    tdata.append(0)
    if header == None:
        nhdata.extend(int_to_bytes(count, "little"))
    if header != None:
        hdata.extend(getLittleJOAAThash(header))
        hdata.extend(int_to_bytes(len(htdata) - 4, "little"))
        hdata.extend(int_to_bytes(count, "little"))
        htdata.extend(header.encode("utf-8"))
        htdata.append(0)

def convertJsonToBjson(fp: str):
    filepath = Path(fp)
    with open(filepath, "r", encoding='utf-8') as f:
        json_file = json.loads(f.read())
    
    structure_data = [0] * 4
    text_data = [0] * 4
    no_headers_data = [0] * 4
    headers_data = [0] * 4
    headers_text_data = [0] * 4

    if type(json_file) == dict:
        addObject(structure_data, text_data, no_headers_data, headers_data, headers_text_data, None, json_file)
    elif type(json_file) == list:
        addList(structure_data, text_data, no_headers_data, headers_data, headers_text_data, None, json_file)
    
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

if __name__ == "__main__":
    convertBjsonToJson("mobs.bjson")
    convertJsonToBjson("mobs_converted.json")