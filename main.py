import json, sys
from conversions import *
from pathlib import Path
from JOAAThash import *

def extract_chunk(data: bytes, idx: int, size: int = 4, start_from: int = 0):
    start = idx * size + start_from
    return data[start:start + size]

filepath = Path("def_action_test.bjson")
with open(filepath, "rb") as f:
    data_bytes = f.read()

json_dict = None
place_dir = []

text_region_idx = int.from_bytes(extract_chunk(data_bytes, 0), "little", signed=False) * 3 + 1
lenght_text_region = int.from_bytes(extract_chunk(data_bytes, text_region_idx), "little", signed=False)
after_region_start = ((text_region_idx + 1) * 4) + lenght_text_region
print(after_region_start)
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
                dir[f"dummy{i}"] = {}
                tmp2 = []
                tmp2.append(dir[f"dummy{i}"])
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
            dir[f"dummy{i}"] = text_part.decode("utf-8")
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
        dir[f"dummy{i}"] = []
        tmp2 = []
        tmp2.append(dir[f"dummy{i}"])
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
            dir[f"dummy{i}"] = float("{:.2f}".format(float_num))
        elif tmp[1] == "list":
            float_num = bytes_to_float(extract_chunk(data_bytes, idx + 1), "little")
            dir.append(float("{:.2f}".format(float_num)))
        tmp[3] += 1
    elif type_extracted == 2:
        tmp = place_dir[-1]
        dir = tmp[0]
        if tmp[1] == "array":
            dir[f"dummy{i}"] = bytes_to_int(extract_chunk(data_bytes, idx + 1), "little")
        elif tmp[1] == "list":
            dir.append(bytes_to_int(extract_chunk(data_bytes, idx + 1), "little"))
        tmp[3] += 1
    elif type_extracted == 1:
        tmp = place_dir[-1]
        dir = tmp[0]
        if tmp[1] == "array":
            bool_num = int.from_bytes(extract_chunk(data_bytes, idx + 1), "little", signed=False)
            if bool_num == 0:
                dir[f"dummy{i}"] = False
            elif bool_num == 1:
                dir[f"dummy{i}"] = True
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

with open(f"{filepath.stem}_test.json", "w") as f:
    f.write(json_string)