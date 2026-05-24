# === configuration.yaml ===
with open('/var/snap/home-assistant-snap/695/configuration.yaml') as f:
    conf = f.read()

# Node names in aktiver_knoten (not the dropdown values)
conf = conf.replace("'Warte Überschuss' %}UEB_W", "'Warte Überschuss' %}UE0")
conf = conf.replace("'Laden 6A' %}UEB_L", "'Laden 6A' %}UE6")

# Transition display text
conf = conf.replace("elif node == 'UEB_W'", "elif node == 'UE0'")
conf = conf.replace("elif node == 'UEB_L'", "elif node == 'UE6'")

conf = conf.replace("node == 'UEB_W' %}mdi:weather", "node == 'UE0' %}mdi:weather")
conf = conf.replace("node == 'UEB_L' %}mdi:ev", "node == 'UE6' %}mdi:ev")

conf = conf.replace("→ UE0  wenn", "→ UE0  wenn")  # already correct after above
conf = conf.replace("→ UEB_L  wenn", "→ UE6  wenn")
conf = conf.replace("→ UEB_W  wenn", "→ UE0  wenn")

conf = conf.replace("von UEB_W (", "von UE0 (")
conf = conf.replace("von UEB_L (", "von UE6 (")
conf = conf.replace("(Warte Überschuss)", "(Warte)")
conf = conf.replace("(Laden 6A)", "(Laden)")

with open('/var/snap/home-assistant-snap/695/configuration.yaml', 'w') as f:
    f.write(conf)

print("✅ configuration.yaml: UEB_W→UE0, UEB_L→UE6")

# === lovelace.entw_algo ===
import json

with open('/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo') as f:
    dash = json.load(f)

card = dash['data']['config']['views'][0]['cards'][3]
content = card['content']

# UEB_W → UE0
content = content.replace('UEB_W["Warte Ueberschuss"]', 'UE0["Warte"]')
content = content.replace('UEB_L["Laden 6A"]', 'UE6["Laden"]')
content = content.replace('UEB_W -->', 'UE0 -->')
content = content.replace('--> UE0_W', '--> UE0')  # This won't match but just in case
content = content.replace('--> UEB_W', '--> UE0')
content = content.replace('--> UEB_L', '--> UE6')
content = content.replace('UEB_L -->', 'UE6 -->')
content = content.replace("class UEB_W ", "class UE0 ")
content = content.replace("class UEB_L ", "class UE6 ")
content = content.replace(",'UEB_W',", ",'UE0',")
content = content.replace(",'UEB_L',", ",'UE6',")

# Fix VBM bug (was 'VM' instead of 'VBM')
content = content.replace(",'VM',", ",'VBM',")

card['content'] = content

with open('/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo', 'w') as f:
    json.dump(dash, f, indent=2)

print("✅ lovelace: UEB_W→UE0, UEB_L→UE6 (VBM-Bug gefixt)")
