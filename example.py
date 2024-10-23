from bjson import BJSONFile

filename = "def_action_test"

bjson_file = BJSONFile().open(f"./{filename}.bjson")
json_str = bjson_file.toJson(showDebug=True)

with open(f"./{filename}.json", "w", encoding="utf-8") as f:
    f.write(json_str)