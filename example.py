from bjson import BJSONFile
from jsontobjson_legacy import convertJsonToBjson_legacy

filename = "your_file"

bjson_file = BJSONFile().open(f"./{filename}.bjson")
json_str = bjson_file.toJson(showDebug=True)

with open(f"./{filename}.json", "w", encoding="utf-8") as f:
    f.write(json_str)

bjson_file.fromJson(json_str)

with open(f"./{filename}_converted_new.bjson", "wb") as f:
    f.write(bjson_file.getData())

convertJsonToBjson_legacy(f"./{filename}.json")