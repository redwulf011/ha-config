# === configuration.yaml ===
with open('/var/snap/home-assistant-snap/695/configuration.yaml') as f:
    conf = f.read()

old_s3_sensor = '''      - name: "Sim S3 Eff Ueberschuss"
        unique_id: sim_s3_eff_ueberschuss
        unit_of_measurement: "kW"
        device_class: power
        state: >
          {% set mode = states('input_select.sim_s3_modus') %}
          {% if mode == 'Manual' %}
            {{ states('input_number.sim_s3_ueberschuss') | float(0) }}
          {% else %}
            {{ states('sensor.pv_uberschuss') | float(0) }}
          {% endif %}

'''

conf = conf.replace(old_s3_sensor, '')

with open('/var/snap/home-assistant-snap/695/configuration.yaml', 'w') as f:
    f.write(conf)

print('✅ sim_s3_eff_ueberschuss aus configuration.yaml entfernt')

# === automations.yaml ===
with open('/var/snap/home-assistant-snap/695/automations.yaml') as f:
    auto = f.read()

old_s3_sync1 = '''    - action: input_number.set_value
      target:
        entity_id: input_number.sim_s3_ueberschuss
      data:
        value: "{{ states('sensor.pv_uberschuss') | float(0) | round(2) }}"
    - action: input_select.select_option
      target:
        entity_id: input_select.sim_connector'''

new_s3_sync1 = '''    - action: input_select.select_option
      target:
        entity_id: input_select.sim_connector'''

auto = auto.replace(old_s3_sync1, new_s3_sync1)

old_s3_sync2 = '''    - action: input_number.set_value
      target:
        entity_id: input_number.sim_s3_ueberschuss
      data:
        value: "{{ states('sensor.pv_uberschuss') | float(0) | round(2) }}"
    - action: input_select.select_option
      target:
        entity_id: input_select.sim_connector
      data:
        option: "{{ states('sensor.vestel_ev_status_connector') }}"'''

new_s3_sync2 = '''    - action: input_select.select_option
      target:
        entity_id: input_select.sim_connector
      data:
        option: "{{ states('sensor.vestel_ev_status_connector') }}"'''

auto = auto.replace(old_s3_sync2, new_s3_sync2)

with open('/var/snap/home-assistant-snap/695/automations.yaml', 'w') as f:
    f.write(auto)

print('✅ sim_s3_ueberschuss aus automations.yaml entfernt')
