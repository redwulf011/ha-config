import json, re

# === 1. configuration.yaml ===
with open('/var/snap/home-assistant-snap/695/configuration.yaml') as f:
    conf = f.read()

# Remove algorithmus_phase block
conf = conf.replace('''      - name: "Algorithmus Phase"
        unique_id: algorithmus_phase
        state: >
          {% set conn = states('sensor.vestel_ev_status_connector') %}
          {% set laden = states('switch.vestel_ev_charge_control') %}
          {% set netz = states('sensor.envoy_122323101510_aktueller_nettostromverbrauch') | float(0) %}
          {% set ue = (netz * -1) | round(1) %}
          {% if conn == 'Available' %}
            {% if ue >= 1.5 and laden == 'off' %}🔌 Auto einstecken! {{ ue }}kW Überschuss{% else %}🔌 Nicht eingesteckt{% endif %}
          {% elif laden == 'on' %}
            {% if ue < 0.5 %}⚡ Lädt - Stopp bei <0,5kW (aktuell {{ ue }}kW){% else %}⚡ Lädt mit {{ states('number.vestel_ev_maximum_current') }}A bei {{ ue }}kW Überschuss{% endif %}
          {% elif conn == 'Preparing' %}
            {% if ue >= 1.5 %}⏳ Bereit - Start bei ≥1,5kW für 1 Min (aktuell {{ ue }}kW) - Zählt...{% else %}⏳ Bereit - Warte auf ≥1,5kW (aktuell {{ ue }}kW){% endif %}
          {% elif conn == 'Charging' %}
            ⚡ Lädt
          {% elif conn == 'Finishing' %}
            ✅ Fertig
          {% else %}
            ⏸️ Pausiert
          {% endif %}
        icon: >
          {% set s = states('sensor.vestel_ev_status_connector') %}
          {% if s == 'Charging' %}mdi:ev-station{% elif s == 'Preparing' %}mdi:power-plug{% elif s == 'Available' %}mdi:power-plug-off{% else %}mdi:help-circle{% endif %}

''', '')

# Remove algorithmus_zustand block
conf = conf.replace('''      - name: "Algorithmus Zustand"
        unique_id: algorithmus_zustand
        state: >
          {% set conn = states('sensor.vestel_ev_status_connector') %}
          {% set laden = states('switch.vestel_ev_charge_control') %}
          {% set netz = states('sensor.envoy_122323101510_aktueller_nettostromverbrauch') | float(0) %}
          {% set ue = (netz * -1) | round(1) %}
          {% if conn == 'Available' %}Leer{% elif conn == 'Finishing' or conn == 'Preparing' %}
            {% if laden == 'on' and ue < 0.3 %}StopZaehler{% elif laden == 'on' %}Laden{% elif ue >= 1.5 %}StartZaehler{% else %}WartenSonne{% endif %}
          {% elif laden == 'on' and ue < 0.3 %}StopZaehler{% elif laden == 'on' %}Laden{% elif laden == 'off' %}Aus{% else %}Unbekannt{% endif %}
        icon: >
          {% set z = states('sensor.algorithmus_zustand') %}
          {% if z == 'Laden' %}mdi:ev-station{% elif z == 'StopZaehler' %}mdi:timer-outline{% elif z == 'StartZaehler' %}mdi:timer-play{% elif z == 'WartenSonne' %}mdi:weather-sunny-off{% elif z == 'Leer' %}mdi:power-plug-off{% else %}mdi:help-circle{% endif %}

''', '')

# Update aktiver_knoten to inline algorithmus_status, then remove algorithmus_status
old_aktiver = '''      - name: "Aktiver Knoten"
        unique_id: aktiver_knoten
        state: >
          {% set s = states('sensor.algorithmus_status') %}
          {% if s == 'Aus' %}AUS
          {% elif s == 'Sofortladen' %}SOF
          {% elif s == 'Ueberschussladen' %}
            {% set sub = states('input_select.sim_algo_zustand') %}
            {% if sub == 'Warte Überschuss' %}UEB_W
            {% elif sub == 'Laden 6A' %}UEB_L
            {% else %}UEB{% endif %}
          {% elif s == 'VollBisMorgen' %}VM
          {% else %}AUS{% endif %}'''

new_aktiver = '''      - name: "Aktiver Knoten"
        unique_id: aktiver_knoten
        state: >
          {% set bt = states('input_select.sim_betriebsart') %}
          {% if bt == 'Aus' %}AUS
          {% elif bt == 'Sofortladen 16A' %}SOF
          {% elif bt == 'Ueberschussladen' %}
            {% set sub = states('input_select.sim_algo_zustand') %}
            {% if sub == 'Warte Überschuss' %}UEB_W
            {% elif sub == 'Laden 6A' %}UEB_L
            {% else %}UEB{% endif %}
          {% elif bt == 'Voll bis Morgen' %}VM
          {% else %}AUS{% endif %}'''

conf = conf.replace(old_aktiver, new_aktiver)

# Remove algorithmus_status block
conf = conf.replace('''      # === Algorithmus Zustandsautomat ===
      - name: "Algorithmus Status"
        unique_id: algorithmus_status
        state: >
          {% set bt = states('input_select.sim_betriebsart') %}
          {% if bt == 'Aus' %}Aus
          {% elif bt == 'Sofortladen 16A' %}Sofortladen
          {% elif bt == 'Ueberschussladen' %}Ueberschussladen
          {% elif bt == 'Voll bis Morgen' %}VollBisMorgen
          {% else %}Unbekannt{% endif %}

''', '')

with open('/var/snap/home-assistant-snap/695/configuration.yaml', 'w') as f:
    f.write(conf)
print("✅ configuration.yaml updated")

# === 2. lovelace dashboard ===
with open('/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo') as f:
    dash = json.load(f)

card2 = dash['data']['config']['views'][0]['cards'][2]
# Remove indices 2,3,4 (algorithmus_zustand, algorithmus_phase, algorithmus_status)
# Remove by filtering
card2['entities'] = [e for e in card2['entities'] if e['entity'] not in [
    'sensor.algorithmus_zustand', 'sensor.algorithmus_phase', 'sensor.algorithmus_status'
]]

with open('/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo', 'w') as f:
    json.dump(dash, f, indent=2)
print("✅ lovelace dashboard updated")

# Verify
print(f"\nVerification:")
print(f"  algorithmus_phase in conf: {'algorithmus_phase' in conf}")
print(f"  algorithmus_zustand in conf: {'algorithmus_zustand' in conf}")
print(f"  algorithmus_status in conf: {'algorithmus_status' in conf}")
print(f"  aktiver_knoten in conf: {'aktiver_knoten' in conf}")
