# Copyright (C) 2025 STBrian
# This file is part of 'pyBjson' and is licensed under the GPLv3.
# See <https://www.gnu.org/licenses/> for details.

from typing import List

try:
    from .bjsonStructures import BJSONRegions, StructEntry, Tracking, HeaderEntry
    from .string_hash import get_JOAAT_hash
except:
    from bjsonStructures import BJSONRegions, StructEntry, Tracking, HeaderEntry
    from string_hash import get_JOAAT_hash

def sortHashMinMax(headerHashes: List[HeaderEntry]):
    n = len(headerHashes)

    for i in range(n):
        already_sorted = True

        for j in range(n - i - 1):
            if headerHashes[j].stringHash > headerHashes[j+1].stringHash:
                headerHashes[j], headerHashes[j+1] = headerHashes[j+1], headerHashes[j]

                already_sorted = False

        if already_sorted:
            break
    return

def appendHeader(header: str, g_count: int, lenHTData: int, headerHashes: List[HeaderEntry]):
    element = HeaderEntry()
    element.stringHash = get_JOAAT_hash(header.lower().encode("utf-8"))
    element.stringPosition = lenHTData
    element.headerIndex = g_count
    headerHashes.append(element)
    return True

def addObject(regions: BJSONRegions, data: dict, track: Tracking):
    local_header_data: List[HeaderEntry] = []
    local_idx = track.item_idx
    for key in data:
        track.item_idx += 1
        if not appendHeader(key, track.item_idx, len(regions.joinedHeaderStrings), local_header_data):
            raise ValueError(f"Missing hash value for: {key}")
        regions.joinedHeaderStrings += key.encode("utf-8") + b'\0'

        if type(data[key]) == type(None):
            regions.structre.append(StructEntry(0, None, 0))
        elif type(data[key]) == bool:
            regions.structre.append(StructEntry(1, data[key], 0))
        elif type(data[key]) == int:
            regions.structre.append(StructEntry(2, data[key], 0))
        elif type(data[key]) == float:
            regions.structre.append(StructEntry(3, data[key], 0))
        elif type(data[key]) == list:
            regions.structre.append(StructEntry(4, len(data[key]), 0))
            addList(regions, data[key], track)
        elif type(data[key]) == str:
            hash_value = get_JOAAT_hash(data[key].lower().encode("utf-8"))
            regions.structre.append(StructEntry(5, hash_value, len(regions.joinedStrings)))
            regions.joinedStrings += data[key].encode('utf-8') + b'\0'
        elif type(data[key]) == dict:
            regions.structre.append(StructEntry(6, len(data[key]), 0))
            addObject(regions, data[key], track)
    
    if len(data) > 0:
        regions.structre[local_idx].value2 = track.objects_lenght
        track.objects_lenght += len(data)
        sortHashMinMax(local_header_data)
        regions.headerIndexes.extend(local_header_data)
    return

def addList(regions: BJSONRegions, data: list, track: Tracking):
    local_array_indexes = []
    local_idx = track.item_idx
    for element in data:
        track.item_idx += 1
        local_array_indexes.append(track.item_idx)

        if type(element) == type(None):
            regions.structre.append(StructEntry(0, None, 0))
        elif type(element) == bool:
            regions.structre.append(StructEntry(1, element, 0))
        elif type(element) == int:
            regions.structre.append(StructEntry(2, element, 0))
        elif type(element) == float:
            regions.structre.append(StructEntry(3, element, 0))
        elif type(element) == list:
            regions.structre.append(StructEntry(4, len(element), 0))
            addList(regions, element, track)
        elif type(element) == str:
            hash_value = get_JOAAT_hash(element.lower().encode("utf-8"))
            regions.structre.append(StructEntry(5, hash_value, len(regions.joinedStrings)))
            regions.joinedStrings += element.encode('utf-8') + b'\0'
        elif type(element) == dict:
            regions.structre.append(StructEntry(6, len(element), 0))
            addObject(regions, element, track)

    regions.structre[local_idx].value2 = track.arrays_lenght
    track.arrays_lenght += len(data)
    regions.arrayIndexes.extend(local_array_indexes)
    return