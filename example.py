from jsontobjson_legacy import convertJsonToBjson_legacy
from bjsontojson_legacy import convertBjsonToJson_legacy

file = "mobs"

'''json_str = convertBjsonToJson_legacy(f"./{file}.bjson")

if not json_str:
    print("Cannot convert bjson to json")
else:
    with open(f"./{file}.json", "w", encoding="utf-8") as f:
        f.write(json_str)'''

success = convertJsonToBjson_legacy(f"./{file}.json")
if not success[0]:
    print("Cannot convert json to bjson")
