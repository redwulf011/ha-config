with open('/var/snap/home-assistant-snap/695/automations.yaml') as f:
    conf = f.read()

# === 1. SUB - Warte → Laden 6A (Start) ===
old_start_triggers = '''  trigger:
    - platform: state
      entity_id: input_select.sim_algo_zustand
      to: "Warte Überschuss"
    - platform: state
      entity_id: sensor.sim_ueberschuss
    - platform: state
      entity_id: sensor.sim_eff_batterie'''

new_start_triggers = '''  trigger:
    - platform: state
      entity_id: input_select.sim_algo_zustand
      to: "Warte Überschuss"
    - platform: state
      entity_id: sensor.sim_netz'''

conf = conf.replace(old_start_triggers, new_start_triggers)

old_start_cond = '''      value_template: >
        {% set ueb = states('sensor.sim_ueberschuss') | float(0) %}
        {% set bat = states('sensor.sim_eff_batterie') | float(0) %}
        {% set soc = states('sensor.sim_eff_soc') | float(0) %}
        {% set net = ueb - bat %}
        {% if soc < 80 %}
          {{ net >= 4.24 }}
        {% else %}
          {{ net >= 4.14 }}'''

new_start_cond = '''      value_template: >
        {% set netz = states('sensor.sim_netz') | float(0) %}
        {% set soc = states('sensor.sim_eff_soc') | float(0) %}
        {% if soc < 80 %}
          {{ netz <= -4.24 }}
        {% else %}
          {{ netz <= -4.14 }}'''

conf = conf.replace(old_start_cond, new_start_cond)

# === 2. SUB - Laden 6A → Warte (Stop) ===
old_stop_triggers = '''  trigger:
    - platform: state
      entity_id: input_select.sim_algo_zustand
      to: "Laden 6A"
    - platform: state
      entity_id: sensor.sim_ueberschuss
    - platform: state
      entity_id: sensor.sim_eff_batterie'''

new_stop_triggers = '''  trigger:
    - platform: state
      entity_id: input_select.sim_algo_zustand
      to: "Laden 6A"
    - platform: state
      entity_id: sensor.sim_netz'''

conf = conf.replace(old_stop_triggers, new_stop_triggers)

old_stop_cond = '''      value_template: >
        {% set ueb = states('sensor.sim_ueberschuss') | float(0) %}
        {% set bat = states('sensor.sim_eff_batterie') | float(0) %}
        {% set net = ueb - bat %}
        {{ net < 0 }}'''

new_stop_cond = '''      value_template: >
        {% set netz = states('sensor.sim_netz') | float(0) %}
        {{ netz >= 0 }}'''

conf = conf.replace(old_stop_cond, new_stop_cond)

with open('/var/snap/home-assistant-snap/695/automations.yaml', 'w') as f:
    f.write(conf)

print('✅ Automations auf sim_netz umgestellt')
