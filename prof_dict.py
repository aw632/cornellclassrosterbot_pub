import json

profDictionary = {}

j = json.dumps(profDictionary)
with open("profDictionary.json", "w") as f:
    f.write(j)
    f.close()
