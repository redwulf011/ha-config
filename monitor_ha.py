#!/usr/bin/env python3
"""HA Zustandsüberwachung – meldet nur relevante Änderungen"""
import json, time, subprocess, sys
from datetime import datetime

TOKEN = open('/home/w/.openclaw/workspace/ha_token.txt').read().strip()
URL = 'http://localhost:8123/api/states/'
ENTITIES = [
    'input_number.sim_netz',
    'sensor.sim_eff_soc',
    'input_select.sim_algo_zustand',
    'sensor.aktiver_knoten',
    'input_number.sim_pv_erzeugung',
    'input_number.sim_hausverbrauch',
    'input_number.sim_batterie_leistung',
]

def get_states():
    try:
        results = {}
        for eid in ENTITIES:
            r = subprocess.run(
                ['curl', '-s', '-H', f'Authorization: Bearer {TOKEN}', URL + eid],
                capture_output=True, text=True, timeout=10
            )
            d = json.loads(r.stdout)
            results[eid] = d['state']
        return results
    except:
        return None

last_node = None
last_algo = None
status_interval = 120  # Sekunden
last_status = 0

print(f"=== Überwachung gestartet {datetime.now().strftime('%H:%M')} ===", flush=True)

while True:
    states = get_states()
    if states is None:
        time.sleep(30)
        continue

    node = states.get('sensor.aktiver_knoten', '?')
    algo = states.get('input_select.sim_algo_zustand', '?')
    netz = states.get('input_number.sim_netz', '?')
    soc = states.get('sensor.sim_eff_soc', '?')
    pv = states.get('input_number.sim_pv_erzeugung', '?')
    haus = states.get('input_number.sim_hausverbrauch', '?')
    batt = states.get('input_number.sim_batterie_leistung', '?')
    now = time.time()

    # Zustandswechsel
    if node != last_node and last_node is not None:
        print(f"🔀 {last_node} → {node} | netz={netz} SoC={soc}% PV={pv} Haus={haus} Batt={batt}", flush=True)
    elif algo != last_algo and last_algo is not None and node == last_node:
        print(f"📌 {algo} | netz={netz} SoC={soc}%", flush=True)

    # Regelmäßiger Status (alle 2 Minuten)
    if now - last_status >= 120:
        print(f"📊 {node} {algo} | netz={netz} SoC={soc}% PV={pv} Haus={haus} Batt={batt}", flush=True)
        last_status = now

    last_node = node
    last_algo = algo
    time.sleep(30)
