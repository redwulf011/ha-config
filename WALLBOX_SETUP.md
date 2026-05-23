# Vestel EVC04 + Home Assistant + Enphase Überschussladen Setup

## Phase 1: Wallbox OCPP Configuration

### Step 1: Access the Wallbox Web Interface
1. Find the wallbox's IP address:
   - Check your router's device list
   - Or look at the wallbox display/app
2. Open browser: `http://<wallbox-ip>`
3. Login (default credentials in manual if needed)

### Step 2: Configure OCPP Settings
Navigate to: **Settings → OCPP**

Fill in these required fields:
- **Central System Address:** `ws://<your-home-assistant-ip>:9000`
  - If HA is on the same network, use internal IP (e.g., `ws://192.168.1.x:9000`)
  - Replace `<your-home-assistant-ip>` with your HA server's IP
  
- **Charge Point Identity:** (any ID, e.g., `vestel-ev` or `charger-1`)

Optional but recommended:
- Set OCPP Security Profile to **Profile 2** (TLS authentication)
- Click "Set to Defaults" if unsure about other parameters

**Save and reboot the wallbox** — it will try to connect to HA's OCPP server

---

## Phase 2: Home Assistant Setup

### Step 1: Install HACS (if not already done)
1. Go to **Settings → Add-ons → Add-on Store** (if using Home Assistant OS)
2. Search `HACS` and install
3. Restart Home Assistant
4. Follow the HACS setup wizard

### Step 2: Install OCPP Integration via HACS
1. Open HACS (click the hamburger menu → HACS)
2. Click **Integrations**
3. Click **+ Create New Repository** (top right)
4. Paste: `https://github.com/lbbrhzn/ocpp`
5. Select category: **Integration**
6. Click **Install**
7. Restart Home Assistant

### Step 3: Add OCPP Integration to HA
1. Go to **Settings → Devices & Services → Integrations**
2. Click **+ Create Integration**
3. Search for `OCPP`
4. Configure:
   - **Central System Host:** `0.0.0.0` (listen on all interfaces)
   - **Central System Port:** `9000` (must match wallbox config)
   - **Central System Identity:** (any name, e.g., `home-assistant`)
   - **Charge Point Identity:** (match or similar to wallbox setting)
5. Click **Create**

**The wallbox should now connect** — you'll see it in HA as a new device.

---

## Phase 3: Enphase Integration

### Step 1: Install Enphase Integration
1. **Settings → Devices & Services → Integrations**
2. Click **+ Create Integration**
3. Search `Enphase`
4. Follow setup (will need your Enphase account)

Once connected, you'll have sensors like:
- `sensor.enphase_current_power` (or similar)
- Other production/consumption data

### Step 2: Find the Right Sensor
The Überschussladen needs to know:
- **Current solar production** (Watts)
- **Current home consumption** (Watts) — if available
- Calculate **excess** = production - consumption

Write down the sensor names that will be used in automations.

---

## Phase 4: Überschussladen Automation

### Verwendete Entitäten (angepasst an Wolfgangs Setup)

**Enphase Envoy (Solar):**
- `sensor.envoy_122323101510_aktuelle_stromproduktion` — Solarproduktion (kW)
- `sensor.envoy_122323101510_aktueller_stromverbrauch` — Hausverbrauch (kW)
- `sensor.envoy_122323101510_ausgeglichene_nettoleistungsaufnahme` — Netto (kW, negativ = Überschuss)

**Wallbox (Vestel EVC04):**
- `switch.vestel_ev_charge_control` — Laden Ein/Aus
- `number.vestel_ev_maximum_current` — Max Strom (A)
- `sensor.vestel_ev_status` — Status

### Fertige Automatisierung

In HA unter **Einstellungen → Automatisierungen → "+ Automatisierung erstellen"** dann oben rechts die **Drei Punkte (⋮) → YAML bearbeiten** und Folgendes einfügen:

```yaml
alias: "Überschussladen - Start bei Solarüberschuss"
description: "Startet Laden wenn 1,5kW+ Solarüberschuss für 2 Minuten anliegt"

trigger:
  - platform: numeric_state
    entity_id: sensor.envoy_122323101510_ausgeglichene_nettoleistungsaufnahme
    below: -1.5  # 1,5 kW negativ = Überschuss
    for:
      minutes: 2

condition:
  - condition: state
    entity_id: switch.vestel_ev_charge_control
    state: "off"

action:
  - action: number.set_value
    target:
      entity_id: number.vestel_ev_maximum_current
    data:
      value: 16
  - action: switch.turn_on
    target:
      entity_id: switch.vestel_ev_charge_control

---

alias: "Überschussladen - Stop bei wenig Sonne"
description: "Stoppt Laden wenn Überschuss unter 0,5kW fällt für 5 Minuten"

trigger:
  - platform: numeric_state
    entity_id: sensor.envoy_122323101510_ausgeglichene_nettoleistungsaufnahme
    above: -0.5  # Weniger als 0,5kW Überschuss
    for:
      minutes: 5

condition:
  - condition: state
    entity_id: switch.vestel_ev_charge_control
    state: "on"

action:
  - action: switch.turn_off
    target:
      entity_id: switch.vestel_ev_charge_control
```

### So importierst du die Automation:
1. HA öffnen → **Einstellungen → Automatisierungen & Szenen**
2. Unten links **"+ Automatisierung erstellen"**
3. Oben rechts **Drei Punkte (⋮) → "YAML bearbeiten"**
4. Vorhandenen Code löschen und obiges YAML einfügen
5. **Speichern**

**Wichtig:** Die `ausgeglichene_nettoleistungsaufnahme` ist negativ bei Solarüberschuss (Einspeisung ins Netz). Deshalb:
- **Start:** `below: -1.5` (1,5 kW+ Überschuss)
- **Stop:** `above: -0.5` (weniger als 0,5 kW Überschuss)

### Finding the Exact OCPP Entity Names
After the wallbox connects, check:
1. **Developer Tools → States** in HA
2. Search for `charger` — you'll see all available entities
3. Use the exact entity names in your automations

---

## Checklist

- [x] Wallbox IP address identified (`192.168.178.102`)
- [x] HA IP identified (`192.168.178.37`)
- [x] Enphase Envoy IP identified (`192.168.178.121`)
- [x] Enphase integration installed and connected
- [x] HACS installed in HA
- [x] OCPP integration installed (lbbrhzn/ocpp v0.10.15)
- [x] OCPP integration added to HA (port 9000, SSL off)
- [x] Wallbox OCPP configured (`ws://192.168.178.37:9000`, ID: `vestel_ev`)
- [x] Wallbox appears in HA as a device ✅
- [x] Automation created: Start bei Solarüberschuss
- [x] Automation created: Stop bei wenig Sonne
- [ ] **Test:** Prüfen ob Laden startet/stoppt bei Sonne ☀️

---

## Troubleshooting

**Wallbox not connecting?**
- Verify Central System Address format: `ws://<ip>:9000` (not `http://`)
- Confirm both on same network
- Check HA OCPP integration is running (**Settings → System → Services → Check OCPP**)

**Sensors missing?**
- Check HA logs for errors
- Verify Enphase integration credentials
- Refresh browser (Ctrl+Shift+R)

**Charging not triggering?**
- Verify sensor names match exactly (case-sensitive)
- Test automations manually in **Developer Tools → Actions**
- Add logging to see what values are being read

---

## Notes

- **Wallbox IP:** _(fill in after discovery)_
- **Home Assistant IP:** _(your HA server IP)_
- **Enphase System ID:** _(if needed)_
- **Solar Threshold:** Start at 2000W, adjust based on preference
- **Max Charging Amps:** 16A for 11kW (adjust for your setup)
