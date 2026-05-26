aut_path = '/var/snap/home-assistant-snap/695/automations.yaml'

with open(aut_path) as f:
    aut = f.read()

# 1) Leeren Trigger aus sub_laden_zu_warte entfernen
#    "    - platform: state\n      entity_id: input_select.sim_algo_zustand\n"
#    ABER NUR wenn danach kein "to:" kommt (also der leere)
old = "    - platform: state\n      entity_id: input_select.sim_algo_zustand\n    - platform: state\n      entity_id: input_number.sim_netz"
new = "    - platform: state\n      entity_id: input_number.sim_netz"
aut = aut.replace(old, new)

# 2) Leere Condition aus der OR-Bedingung entfernen
#    "        - condition: state\n          entity_id: input_select.sim_algo_zustand\n"
#    direkt nach der "Laden 6A" condition
old = "          state: \"Laden 6A\"\n        - condition: state\n          entity_id: input_select.sim_algo_zustand\n    - condition: template"
new = "          state: \"Laden 6A\"\n    - condition: template"
aut = aut.replace(old, new)

with open(aut_path, 'w') as f:
    f.write(aut)

print("✅ automations.yaml repariert")

# Verify
with open(aut_path) as f:
    content = f.read()
# Prüfen ob noch leere platform/condition Blöcke da sind  
import re
empty_trigger = re.findall(r"    - platform: state\n      entity_id: input_select\.sim_algo_zustand\n    - platform: state", content)
print(f"Leere Trigger gefunden: {len(empty_trigger)}")
