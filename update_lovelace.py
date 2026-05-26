import json

path = '/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo'

with open(path) as f:
    data = json.load(f)

card = data['data']['config']['views'][0]['cards'][3]

new_content = '''flowchart LR
    AUS["Aus"]
    SOF["Sofortladen"]
    UE0["Warte"]
    UE6["Laden"]
    UE6+["Laden+"]
    VBM["VollBisMorgen"]

    UE0 -->|"sim_netz ≤ -4.24 (SoC<80%) / ≤ -4.14 (SoC≥80%)"| UE6
    UE6 -->|"10s"| UE6+
    UE6 -->|"sim_netz ≥ 0 (SoC<80%) / ≥ 0.1 (SoC≥80%)"| UE0
    UE6+ -->|"sim_netz ≥ 0 (SoC<80%) / ≥ 0.1 (SoC≥80%)"| UE0

    classDef active fill:#4CAF50,color:white,stroke:#2E7D32,stroke-width:3px
    classDef inactive fill:#e0e0e0,color:#666,stroke:#bbb

    class AUS ${if(is_state('sensor.aktiver_knoten','AUS'),'active','inactive')}
    class SOF ${if(is_state('sensor.aktiver_knoten','SOF'),'active','inactive')}
    class UE0 ${if(is_state('sensor.aktiver_knoten','UE0'),'active','inactive')}
    class UE6 ${if(is_state('sensor.aktiver_knoten','UE6'),'active','inactive')}
    class UE6+ ${if(is_state('sensor.aktiver_knoten','UE6+'),'active','inactive')}
    class VBM ${if(is_state('sensor.aktiver_knoten','VBM'),'active','inactive')}'''

card['content'] = new_content

with open(path, 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Updated Schicht 4 diagram - removed Betriebsart-switching arrows")
