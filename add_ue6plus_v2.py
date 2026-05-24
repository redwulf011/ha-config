import json

# === 1. Add "Laden 6A+" to input_select options ===
with open('/var/snap/home-assistant-snap/695/.storage/core.restore_state') as f:
    data = json.load(f)

items = data.get('data', [])
for item in items:
    if isinstance(item, dict):
        state = item.get('state', {})
        if state.get('entity_id') == 'input_select.sim_algo_zustand':
            attrs = state.get('attributes', {})
            if 'Laden 6A+' not in attrs.get('options', []):
                attrs['options'] = ['Warte Überschuss', 'Laden 6A', 'Laden 6A+']
                state['attributes'] = attrs
            break

with open('/var/snap/home-assistant-snap/695/.storage/core.restore_state', 'w') as f:
    json.dump(data, f, indent=2)
print("✅ Option 'Laden 6A+' zu input_select hinzugefügt")

# === 2. configuration.yaml: aktiver_knoten & aktuelle_uebergaenge ===
with open('/var/snap/home-assistant-snap/695/configuration.yaml') as f:
    conf = f.read()

# aktiver_knoten: add UE6+ mapping
conf = conf.replace(
    "{% elif sub == 'Laden 6A' %}UE6\n          {% else %}UEB",
    "{% elif sub == 'Laden 6A' %}UE6\n          {% elif sub == 'Laden 6A+' %}UE6+\n          {% else %}UEB"
)

# aktuelle_uebergaenge: add UE6+ section (copy of UE6 with name change)
conf = conf.replace(
    "{% elif node == 'UE6' %}\n            🔄 Übergänge von UE6 (Laden):",
    "{% elif node == 'UE6' %}\n            🔄 Übergänge von UE6 (Laden):\n          {% elif node == 'UE6+' %}\n            🔄 Übergänge von UE6+ (Laden+):"
)

# Icon: add UE6+ icon
conf = conf.replace(
    "node == 'UE6' %}mdi:ev-station",
    "node == 'UE6' %}mdi:ev-station{% elif node == 'UE6+' %}mdi:ev-station"
)

with open('/var/snap/home-assistant-snap/695/configuration.yaml', 'w') as f:
    f.write(conf)
print("✅ configuration.yaml: UE6+ in aktiver_knoten & aktuelle_uebergaenge")

# === 3. automations.yaml ===
with open('/var/snap/home-assistant-snap/695/automations.yaml') as f:
    auto = f.read()

# Add SUB - UE6 → UE6+ (10s delay) before SUB section
new_auto_block = '''- id: "sub_ue6_zu_ue6plus"
  alias: "SUB - UE6 → UE6+ (10s)"
  mode: single
  trigger:
    - platform: state
      entity_id: input_select.sim_algo_zustand
      to: "Laden 6A"
  condition:
    - condition: state
      entity_id: input_select.sim_algo_zustand
      state: "Laden 6A"
  action:
    - delay:
        seconds: 10
    - condition: state
      entity_id: input_select.sim_algo_zustand
      state: "Laden 6A"
    - action: input_select.select_option
      target:
        entity_id: input_select.sim_algo_zustand
      data:
        option: "Laden 6A+"

'''

auto = auto.replace(
    '\n# === SUB: Eingebetteter Zustandsautomat für Überschussladen ===',
    '\n' + new_auto_block + '# === SUB: Eingebetteter Zustandsautomat für Überschussladen ==='
)

# Update SUB - Laden 6A → Warte trigger to also trigger on "Laden 6A+"
old_trigger = '''  trigger:
    - platform: state
      entity_id: input_select.sim_algo_zustand
      to: "Laden 6A"
    - platform: state
      entity_id: input_number.sim_netz'''

new_trigger = '''  trigger:
    - platform: state
      entity_id: input_select.sim_algo_zustand
      to: "Laden 6A"
    - platform: state
      entity_id: input_select.sim_algo_zustand
      to: "Laden 6A+"
    - platform: state
      entity_id: input_number.sim_netz'''

auto = auto.replace(old_trigger, new_trigger)

# Update condition: "Laden 6A" OR "Laden 6A+"
old_cond = '''    - condition: state
      entity_id: input_select.sim_algo_zustand
      state: "Laden 6A"
    - condition: template'''

new_cond = '''    - condition: or
      conditions:
        - condition: state
          entity_id: input_select.sim_algo_zustand
          state: "Laden 6A"
        - condition: state
          entity_id: input_select.sim_algo_zustand
          state: "Laden 6A+"
    - condition: template'''

auto = auto.replace(old_cond, new_cond)

with open('/var/snap/home-assistant-snap/695/automations.yaml', 'w') as f:
    f.write(auto)
print("✅ automations.yaml: UE6→UE6+ Automation + Stop-Bedingung für UE6+")

# === 4. lovelace: add UE6+ to mermaid ===
with open('/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo') as f:
    dash = json.load(f)

card = dash['data']['config']['views'][0]['cards'][3]
content = card['content']

# Add UE6+ node and transitions (copy of UE6 -> UE6+)
content = content.replace(
    '    UE6["Laden"]',
    '    UE6["Laden"]\n    UE6+["Laden+"]'
)

content = content.replace(
    '    UE6 -->|"sim_netz ≥ 0 (SoC<80%) / ≥ 0.1 (SoC≥80%)"| UE0',
    '    UE6 -->|"10s"| UE6+\n    UE6 -->|"sim_netz ≥ 0 (SoC<80%) / ≥ 0.1 (SoC≥80%)"| UE0\n    UE6+ -->|"sim_netz ≥ 0 (SoC<80%) / ≥ 0.1 (SoC≥80%)"| UE0'
)

# Copy all other UE6 transitions to UE6+
transitions_to_copy = ['AUS', 'SOF', 'VBM']
for target in transitions_to_copy:
    old_line = f'    UE6 --> {target}'
    new_line = f'{old_line}\n    UE6+ --> {target}'
    if old_line in content:
        content = content.replace(old_line, new_line)

# Add CSS class for UE6+
content = content.replace(
    "    class UE6 ${if(is_state('sensor.aktiver_knoten','UE6'),'active','inactive')}",
    "    class UE6 ${if(is_state('sensor.aktiver_knoten','UE6'),'active','inactive')}\n    class UE6+ ${if(is_state('sensor.aktiver_knoten','UE6+'),'active','inactive')}"
)

card['content'] = content

with open('/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo', 'w') as f:
    json.dump(dash, f, indent=2)
print("✅ lovelace: UE6+ im Mermaid-Diagramm")

print("\n✅ ALL DONE")
