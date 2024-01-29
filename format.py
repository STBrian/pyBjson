import json

with open("def_action_test.json", "r") as f:
    json_data = f.read()

json_dict = json.loads(json_data)

json.dump(json_dict, open("def_action_text_formated.json", "w"), indent=4)