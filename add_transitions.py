import json

# ===== 1. Add template sensor to configuration.yaml =====
with open('/var/snap/home-assistant-snap/695/configuration.yaml') as f:
    conf = f.read()

transitions_sensor = '''
      # Übergänge vom aktuellen Zustand (für Dashboard)
      - name: "Aktuelle Übergänge"
        unique_id: aktuelle_uebergaenge
        state: >
          {% set node = states('sensor.aktiver_knoten') %}
          {% set soc = states('sensor.sim_eff_soc') | float(0) %}
          {% set soc_text = '(SoC<' + soc|string + '%)' if soc < 80 else '(SoC≥' + soc|string + '%)' %}
          {% set start_thresh = '4.24' if soc < 80 else '4.14' %}
          {% if node == 'AUS' %}
            🔄 Übergänge von AUS:
            → SOF  wenn Betriebsart = Sofortladen 16A
            → VM   wenn Betriebsart = Voll bis Morgen
            → UEB  wenn Betriebsart = Überschussladen
          {% elif node == 'SOF' %}
            🔄 Übergänge von SOF (Sofortladen):
            → AUS  wenn Betriebsart = Aus
            → VM   wenn Betriebsart = Voll bis Morgen
            → UEB  wenn Betriebsart = Überschussladen
          {% elif node == 'VM' %}
            🔄 Übergänge von VM (Voll bis Morgen):
            → AUS  wenn Betriebsart = Aus
            → SOF  wenn Betriebsart = Sofortladen 16A
            → UEB  wenn Betriebsart = Überschussladen
          {% elif node == 'UEB_W' %}
            🔄 Übergänge von UEB_W (Warte Überschuss):
            → UEB_L  wenn Net ≥ {{ start_thresh }}kW {{ soc_text }}
            → AUS    wenn Betriebsart = Aus
            → SOF    wenn Betriebsart = Sofortladen 16A
            → VM     wenn Betriebsart = Voll bis Morgen
          {% elif node == 'UEB_L' %}
            🔄 Übergänge von UEB_L (Laden 6A):
            → UEB_W  wenn Net < 0
            → AUS    wenn Betriebsart = Aus
            → SOF    wenn Betriebsart = Sofortladen 16A
            → VM     wenn Betriebsart = Voll bis Morgen
          {% else %}
            🔄 Keine Übergänge definiert für {{ node }}
          {% endif %}
        icon: >
          {% set node = states('sensor.aktiver_knoten') %}
          {% if node == 'AUS' %}mdi:power-off{% elif node == 'SOF' %}mdi:lightning-bolt{% elif node == 'VM' %}mdi:weather-night{% elif node == 'UEB_W' %}mdi:weather-sunny{% elif node == 'UEB_L' %}mdi:ev-station{% else %}mdi:help-circle{% endif %}

'''

# Insert before the 'sensor:' line (line 271)
insert_pos = conf.find('\nsensor:\n')
conf = conf[:insert_pos] + transitions_sensor + conf[insert_pos:]

with open('/var/snap/home-assistant-snap/695/configuration.yaml', 'w') as f:
    f.write(conf)
print("✅ configuration.yaml: transitions sensor added")

# ===== 2. Add markdown card to lovelace dashboard =====
with open('/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo') as f:
    dash = json.load(f)

# Add a markdown card after the mermaid card (index 3)
mermaid_card = dash['data']['config']['views'][0]['cards'][3]

transitions_card = {
    "type": "markdown",
    "title": "Aktuelle Übergänge",
    "card_size": 4,
    "content": "{{ states('sensor.aktuelle_uebergaenge') }}"
}

# Insert after the mermaid card
dash['data']['config']['views'][0]['cards'].insert(4, transitions_card)

with open('/var/snap/home-assistant-snap/695/.storage/lovelace.entw_algo', 'w') as f:
    json.dump(dash, f, indent=2)
print("✅ lovelace dashboard: transitions card added")
