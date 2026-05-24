# === configuration.yaml ===
with open('/var/snap/home-assistant-snap/695/configuration.yaml') as f:
    conf = f.read()

old_s3_bat = '''      - name: "Sim S3 Eff Batterie"
        unique_id: sim_s3_eff_batterie
        unit_of_measurement: "kW"
        device_class: power
        state: >
          {% set mode = states('input_select.sim_s3_modus') %}
          {% if mode == 'Manual' %}
            {{ states('input_number.sim_s3_batterie') | float(0) }}
          {% else %}
            {{ states('sensor.envoy_batterieleistung') | float(0) }}
          {% endif %}

'''

conf = conf.replace(old_s3_bat, '')
with open('/var/snap/home-assistant-snap/695/configuration.yaml', 'w') as f:
    f.write(conf)
print('✅ sim_s3_eff_batterie aus configuration.yaml entfernt')

# === automations.yaml ===
with open('/var/snap/home-assistant-snap/695/automations.yaml') as f:
    auto = f.read()

# Remove sim_s3_batterie setter from sim_auto_sync_slider
auto = auto.replace('''    - action: input_number.set_value
      target:
        entity_id: input_number.sim_s3_batterie
      data:
        value: "{{ states('sensor.envoy_batterieleistung') | float(0) | round(2) }}"
    - action: input_select.select_option
      target:
        entity_id: input_select.sim_connector
      data:
        option: "{{ states('sensor.vestel_ev_status_connector') }}"
    - choose:''', '''    - action: input_select.select_option
      target:
        entity_id: input_select.sim_connector
      data:
        option: "{{ states('sensor.vestel_ev_status_connector') }}"
    - choose:''')

# Remove the entire sim_s3_sync automation
old_s3_sync = '''- id: "sim_s3_sync"
  alias: "SIM - S3 Sync"
  trigger:
    - platform: homeassistant
      event: start
    - platform: time_pattern
      seconds: "/1"
    - platform: state
      entity_id: input_select.sim_s3_modus
      to: Auto
  condition:
    - condition: state
      entity_id: input_select.sim_s3_modus
      state: Auto
  action:
    - action: input_number.set_value
      target:
        entity_id: input_number.sim_s3_batterie
      data:
        value: "{{ states('sensor.envoy_batterieleistung') | float(0) | round(2) }}"
    - action: input_select.select_option
      target:
        entity_id: input_select.sim_connector
      data:
        option: "{{ states('sensor.vestel_ev_status_connector') }}"

'''

auto = auto.replace(old_s3_sync, '')

with open('/var/snap/home-assistant-snap/695/automations.yaml', 'w') as f:
    f.write(auto)
print('✅ sim_s3_sync Automation und sim_s3_batterie entfernt')
