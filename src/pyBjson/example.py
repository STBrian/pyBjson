from bjson import BJSONFile

filename = "mobs"

'''bjson_file = BJSONFile().open(f"./{filename}.bjson")
json_str = bjson_file.toJson(showDebug=True)

with open(f"./{filename}.json", "w", encoding="utf-8") as f:
    f.write(json_str)'''

with open(f"{filename}.json", "r") as f:
    bjson_file = BJSONFile()
    bjson_file.fromJson(f.read())

with open(f"./{filename}_converted_new.bjson", "wb") as f:
    f.write(bjson_file.getData())