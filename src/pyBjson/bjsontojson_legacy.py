# Copyright (C) 2025 STBrian
# This file is part of 'pyBjson' and is licensed under the GPLv3.
# See <https://www.gnu.org/licenses/> for details.

import json
from pathlib import Path

try:
    from .utils import *
    from .updateDatabase import MyDatabase
    from .deprecation_warn import deprecated
except:
    from utils import *
    from updateDatabase import MyDatabase
    from deprecation_warn import deprecated

def getHeaders(data: bytes, hash_database: MyDatabase):
    count = 0
    text_region_start = (int.from_bytes(extract_chunk(data, 0), "little", signed=False) * 3 * 4) + 4
    lenght_text_r = int.from_bytes(extract_chunk(data, 0, 4, text_region_start), "little", signed=False)
    region_start = text_region_start + lenght_text_r + 4
    pre_region_len = int.from_bytes(extract_chunk(data, 0, 4, region_start), "little", signed=False)
    lenght = int.from_bytes(extract_chunk(data, pre_region_len + 1, 4, region_start), "little", signed=False)
    #print(pre_region_len)
    #print(lenght)
    headers = [""] * (lenght + pre_region_len)
    headers_text_start = region_start + (pre_region_len + 1) * 4 + (lenght) * 4 * 3 + 4
    for i in range(pre_region_len):
        idx = int.from_bytes(extract_chunk(data, i + 1, 4, region_start), "little", signed=False)
        headers[idx - 1] = None
    for i in range(lenght):
        idx = pre_region_len + 1 + i * 3 + 1
        hashval = int.from_bytes(extract_chunk(data, idx, 4, region_start), "little")
        headers_idx = int.from_bytes(extract_chunk(data, idx + 1, 4, region_start), "little", signed=False)
        headers_idx_end = headers_text_start + 4 + headers_idx
        while True:
            if data[headers_idx_end] == 0:
                break
            else:
                headers_idx_end += 1
        header_part = data[headers_text_start + 4 + headers_idx:headers_idx_end]
        header_idx = int.from_bytes(extract_chunk(data, idx + 2, 4, region_start), "little", signed=False) # Nota es distinto a headers_idx
        header_decode = header_part.decode('utf-8')
        headers[header_idx - 1] = header_decode
        hash_database.addToDatabase(header_decode, hashval)
        if count < 30:
            print(int.from_bytes(extract_chunk(data, idx, 4, region_start), "little"), extract_chunk(data, idx + 1, 4, region_start).hex(), extract_chunk(data, idx + 2, 4, region_start).hex(), header_decode)
            count += 1
    return headers

@deprecated("Use BJSONFile class method instead")
def convertBjsonToJson(fp: str|Path|None):
    hash_database = MyDatabase("hash_database.json")
    if type(fp) == str:
        filepath = Path(fp)
    elif type(fp) == Path:
        filepath = fp
    else:
        raise ValueError()
    with open(filepath, "rb") as f:
        data_bytes = f.read()

    json_dict = None
    place_dir = []

    text_region_idx = int.from_bytes(extract_chunk(data_bytes, 0), "little", signed=False) * 3 + 1
    #lenght_text_region = int.from_bytes(extract_chunk(data_bytes, text_region_idx), "little", signed=False)
    print("Getting headers...")
    headers = getHeaders(data_bytes, hash_database)
    #sys.exit()

    print("Getting structure...")
    for i in range(int.from_bytes(extract_chunk(data_bytes, 0), "little", signed=False)):
        idx = i * 3 + 1
        type_extracted = int.from_bytes(extract_chunk(data_bytes, idx), "little", signed=False)
        if type_extracted == 6:
            # Object data type
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
                hashval = int.from_bytes(extract_chunk(data_bytes, idx + 1), "little")
                text_idx = int.from_bytes(extract_chunk(data_bytes, idx + 2), "little", signed=False)
                text_idx_end = ((text_region_idx + 1) * 4) + text_idx
                while True:
                    if data_bytes[text_idx_end] == 0:
                        break
                    else:
                        text_idx_end += 1
                text_part = data_bytes[((text_region_idx + 1) * 4) + text_idx:text_idx_end]
                # Header
                text_decode = text_part.decode("utf-8")
                dir[f"{headers[i-1]}"] = text_decode
                hash_database.addToDatabase(text_decode, hashval)
            elif tmp[1] == "list":
                hashlist = list(extract_chunk(data_bytes, idx + 1))
                text_idx = int.from_bytes(extract_chunk(data_bytes, idx + 2), "little", signed=False)
                text_idx_end = ((text_region_idx + 1) * 4) + text_idx
                while True:
                    if data_bytes[text_idx_end] == 0:
                        break
                    else:
                        text_idx_end += 1
                text_part = data_bytes[((text_region_idx + 1) * 4) + text_idx:text_idx_end]
                text_decode = text_part.decode("utf-8")
                dir.append(text_decode)
                hash_database.addToDatabase(text_decode, hashlist)
            tmp[3] += 1
        elif type_extracted == 4:
            # Array data type
            if json_dict == None:
                json_dict = []
                tmp = []
                tmp.append(json_dict)
                tmp.append("list")
                tmp.append(int.from_bytes(extract_chunk(data_bytes, idx + 1), "little", signed=False))
                tmp.append(0)
                place_dir.append(tmp)
            else:
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
            # Float data type
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
            # Integer data type
            tmp = place_dir[-1]
            dir = tmp[0]
            if tmp[1] == "array":
                # Header
                dir[f"{headers[i-1]}"] = bytes_to_int(extract_chunk(data_bytes, idx + 1), "little")
            elif tmp[1] == "list":
                dir.append(bytes_to_int(extract_chunk(data_bytes, idx + 1), "little"))
            tmp[3] += 1
        elif type_extracted == 1:
            # Boolean data type
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
        elif type_extracted == 0:
            # None data type
            tmp = place_dir[-1]
            dir = tmp[0]
            if tmp[1] == "array":
                # With header
                dir[f"{headers[i-1]}"] = None
            elif tmp[1] == "list":
                dir.append(None)
            tmp[3] += 1
        else:
            return

        if len(place_dir) > 0:
            check = place_dir[-1]
            if check[3] >= check[2]:
                place_dir.pop(-1)

    json_string = json.dumps(json_dict, indent=4)
    
    hash_database.save()
    return json_string