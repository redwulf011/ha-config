import json

new_diagram = '''flowchart LR
    AUS["Aus"]
    SOF["Sofortladen"]
    UE0["Warte"]
    UE6["Laden"]
    VBM["VollBisMorgen"]

    UE0 -->|"sim_netz \u2264 -4.24 (SoC<80%) / \u2264 -4.14 (SoC\u226580%)"| UE6
    UE6 -->|"sim_netz \u2265 0 (SoC<80%) / \u2265 0.1 (SoC\u226580%)"| UE0
    UE6 --> AUS
    UE6 --> SOF
    UE6 --> VBM

    classDef active fill:#4CAF50,color:white,stroke:#2E7D32,stroke-width:3px
    classDef inactive fill:#e0e0e0,color:#666,stroke:#bbb

    class AUS ${if(is_state('sensor.aktiver_knoten','AUS'),'active','inactive')}
    class SOF ${if(is_state('sensor.aktiver_knoten','SOF'),'active','inactive')}
    class UE0 ${if(is_state('sensor.aktiver_knoten','UE0'),'active','inactive')}
    class UE6 ${if(is_state('sensor.aktiver_knoten','UE6'),'active','inactive')}
    class VBM ${if(is_state('sensor.aktiver_knoten','VBM'),'active','inactive')}'''

paths = [
    '/home/w/.openclaw/workspace/lovelace.entw_algo',
    '/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo',
]

for path in paths:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    card = data['data']['config']['views'][0]['cards'][3]
    card['content'] = new_diagram
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ {path} aktualisiert")
