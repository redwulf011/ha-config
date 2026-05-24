# === configuration.yaml ===
with open('/var/snap/home-assistant-snap/695/configuration.yaml') as f:
    conf = f.read()

# Replace state identifiers VM → VBM (only where it's a node name, not part of other words)
import re

# In aktiver_knoten template: 'VM' → 'VBM'
conf = conf.replace("{% elif bt == 'Voll bis Morgen' %}VM", "{% elif bt == 'Voll bis Morgen' %}VBM")

# In aktuelle_uebergaenge: node == 'VM' → 'VBM'
conf = conf.replace("{% elif node == 'VM' %}", "{% elif node == 'VBM' %}")
conf = conf.replace("node == 'VM' %}mdi:weather-night", "node == 'VBM' %}mdi:weather-night")

# Display text: → VM → → VBM
conf = conf.replace("→ VM   wenn", "→ VBM  wenn")
conf = conf.replace("→ VM    wenn", "→ VBM   wenn")
conf = conf.replace("→ VM     wenn", "→ VBM    wenn")

# "von VM (" → "von VBM ("
conf = conf.replace("Übergänge von VM (", "Übergänge von VBM (")

with open('/var/snap/home-assistant-snap/695/configuration.yaml', 'w') as f:
    f.write(conf)

print("✅ configuration.yaml: VM → VBM")

# === lovelace.entw_algo ===
import json

with open('/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo') as f:
    dash = json.load(f)

# Update mermaid content
card = dash['data']['config']['views'][0]['cards'][3]
content = card['content']

# Replace VM → VBM in mermaid (careful: VM appears within words too)
# In mermaid: VM["VollBisMorgen"] → VBM["VollBisMorgen"]
content = content.replace('VM["VollBisMorgen"]', 'VBM["VollBisMorgen"]')
# VM connections
content = content.replace('VM -->', 'VBM -->')
content = content.replace('--> VM', '--> VBM')
# VM class
content = content.replace("class VM ", "class VBM ")
content = content.replace(",'VM',", ",'VBM',")

card['content'] = content

with open('/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo', 'w') as f:
    json.dump(dash, f, indent=2)

print("✅ lovelace: VM → VBM")
