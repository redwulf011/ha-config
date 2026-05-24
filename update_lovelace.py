import json

path = '/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo'

with open(path) as f:
    data = json.load(f)

card = data['data']['config']['views'][0]['cards'][3]
old_content = card['content']
new_content = old_content.replace(
    'UEB_L -->|"Net <= 4.14 (SoC<80) / <= 4.04 (SoC>=80)"| UEB_W',
    'UEB_L -->|"Net < 0"| UEB_W'
)
card['content'] = new_content

with open(path, 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Updated stop threshold arrow in Schicht 4")
