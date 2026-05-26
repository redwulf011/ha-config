import re

# =====================================
# 1) automations.yaml
# =====================================
aut_path = '/var/snap/home-assistant-snap/695/automations.yaml'
with open(aut_path) as f:
    aut = f.read()

# SUB - Warte → Laden 6A (Startbedingung)
# Alte Start-Logik (4.24/4.14) → Neue (1.54/2.84 mit SoC≥20%)
old_start = '''      value_template: >
        {% set netz = states('input_number.sim_netz') | float(0) %}
        {% set soc = states('sensor.sim_eff_soc') | float(0) %}
        {% if soc < 80 %}
          {{ netz <= -4.24 }}
        {% else %}
          {{ netz <= -4.14 }}
        {% endif %}
  action:'''

new_start = '''      value_template: >
        {% set netz = states('input_number.sim_netz') | float(0) %}
        {% set soc = states('sensor.sim_eff_soc') | float(0) %}
        {% if soc >= 20 %}
          {{ netz <= -1.54 }}
        {% else %}
          {{ netz <= -2.84 }}
        {% endif %}
  action:'''

aut = aut.replace(old_start, new_start)

# SUB - Laden 6A → Warte (Stopbedingung)
# Alte Stop-Logik (0/0.1 mit SoC<80/≥80) → Neue (-1.3/0 mit SoC≥10/<10)
old_stop = '''      value_template: >
        {% set netz = states('input_number.sim_netz') | float(0) %}
        {% set soc = states('sensor.sim_eff_soc') | float(0) %}
        {% if soc < 80 %}
          {{ netz >= 0 }}
        {% else %}
          {{ netz >= 0.1 }}
        {% endif %}
  action:'''

new_stop = '''      value_template: >
        {% set netz = states('input_number.sim_netz') | float(0) %}
        {% set soc = states('sensor.sim_eff_soc') | float(0) %}
        {% if soc >= 10 %}
          {{ netz >= -1.3 }}
        {% else %}
          {{ netz >= 0 }}
        {% endif %}
  action:'''

aut = aut.replace(old_stop, new_stop)

with open(aut_path, 'w') as f:
    f.write(aut)
print("✅ automations.yaml: Start/Stop Bedingungen aktualisiert")

# =====================================
# 2) configuration.yaml (aktuelle_uebergaenge Texte)
# =====================================
cfg_path = '/var/snap/home-assistant-snap/695/configuration.yaml'
with open(cfg_path) as f:
    cfg = f.read()

# UE0 Übergänge Text aktualisieren
old_ue0 = '            \u2192 UE6  wenn sim_netz \u2264 -{{ start_thresh }}kW {{ soc_text }}'
new_ue0 = '            \u2192 UE6  wenn sim_netz \u2264 -1.54kW (SoC\u226520%) / \u2264 -2.84kW (SoC<20%)'
cfg = cfg.replace(old_ue0, new_ue0)

# UE6 Übergänge Text aktualisieren  
old_ue6 = '            \u2192 UE0  wenn sim_netz \u2265 0 (SoC<80%) / \u2265 0.1 (SoC\u226580%)'
new_ue6 = '            \u2192 UE0  wenn sim_netz \u2265 -1.3kW (SoC\u226510%) / \u2265 0kW (SoC<10%)'
cfg = cfg.replace(old_ue6, new_ue6)

with open(cfg_path, 'w') as f:
    f.write(cfg)
print("✅ configuration.yaml: Übergangs-Texte aktualisiert")

# =====================================
# 3) Verify
# =====================================
with open(aut_path) as f:
    for n, line in enumerate(f, 1):
        if 'netz <= -4.24' in line or 'netz <= -4.14' in line:
            print(f"  ⚠️  Alte Start-Schwelle noch in automations.yaml Zeile {n}")
        if 'netz >= 0' in line and '>= -1.3' not in line and 'SoC' in line:
            if '>= 0.1' not in line:
                print(f"  ⚠️  Alte Stop-Schwelle noch in automations.yaml Zeile {n}")
    print("  ✅ Keine alten Schwellwerte gefunden")

# Automations valide?
import yaml
with open(aut_path) as f:
    try:
        yaml.safe_load(f)
        print("  ✅ automations.yaml YAML valide")
    except Exception as e:
        print(f"  ❌ automations.yaml: {e}")
