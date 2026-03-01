import json
json_path = os.path.join("static", "various", "sample_data.json")
with open(json_path) as f:
    data = json.load(f)
stx.st_code(code=json.dumps(data, indent=2), language="json")
