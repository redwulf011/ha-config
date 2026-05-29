import json

# Hysterese 0.1kW: Start ≤ -0.74, Stop ≥ -0.64

aut_path = '/var/snap/home-assistant-snap/695/automations.yaml'
with open(aut_path) as f:
    aut = f.read()

# UE6→UE7: ≤ -0.74
aut = aut.replace('{{ netz <= -0.79 }}', '{{ netz <= -0.74 }}')
# UE7→UE6: ≥ -0.64
aut = aut.replace('{{ netz >= -0.59 }}', '{{ netz >= -0.64 }}')

with open(aut_path, 'w') as f:
    f.write(aut)
print("✅ automations.yaml")

cfg_path = '/var/snap/home-assistant-snap/695/configuration.yaml'
with open(cfg_path) as f:
    cfg = f.read()

cfg = cfg.replace('\u2192 UE7  wenn sim_netz \u2264 -0.79kW', '\u2192 UE7  wenn sim_netz \u2264 -0.74kW')
cfg = cfg.replace('\u2192 UE6  wenn sim_netz \u2265 -0.59kW', '\u2192 UE6  wenn sim_netz \u2265 -0.64kW')

with open(cfg_path, 'w') as f:
    f.write(cfg)
print("✅ configuration.yaml")

new_diagram = '''flowchart LR
    AUS["Aus"]
    SOF["Sofortladen"]
    UE0["Warte"]
    UE6["Laden 6A"]
    UE7["Laden 7A"]
    VBM["VollBisMorgen"]

    UE0 -->|"sim_netz \u2264 -1.54 (SoC\u226520%) / \u2264 -2.84 (SoC<20%)"| UE6
    UE6 -->|"sim_netz \u2264 -0.74"| UE7
    UE7 -->|"sim_netz \u2265 -0.64"| UE6
    UE6 -->|"sim_netz \u2265 -1.3 (SoC\u226510%) / \u2265 0 (SoC<10%)"| UE0

    classDef active fill:#4CAF50,color:white,stroke:#2E7D32,stroke-width:3px
    classDef inactive fill:#e0e0e0,color:#666,stroke:#bbb

    class AUS ${if(is_state('sensor.aktiver_knoten','AUS'),'active','inactive')}
    class SOF ${if(is_state('sensor.aktiver_knoten','SOF'),'active','inactive')}
    class UE0 ${if(is_state('sensor.aktiver_knoten','UE0'),'active','inactive')}
    class UE6 ${if(is_state('sensor.aktiver_knoten','UE6'),'active','inactive')}
    class UE7 ${if(is_state('sensor.aktiver_knoten','UE7'),'active','inactive')}
    class VBM ${if(is_state('sensor.aktiver_knoten','VBM'),'active','inactive')}'''

paths = [
    '/home/w/.openclaw/workspace/lovelace.entw_algo',
    '/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo',
]
for path in paths:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    data['data']['config']['views'][0]['cards'][3]['content'] = new_diagram
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
print("✅ Mermaid")
