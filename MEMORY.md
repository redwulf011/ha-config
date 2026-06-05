# MEMORY.md - OpenClaw's Continuity

## Current Project: EV Charger Automation

**Goal:** Set up Überschussladen (excess solar charging) for Vestel EVC04 via Home Assistant + Enphase

**Hardware:**
- Vestel EVC04-AC11SW-T2P (11kW wallbox, 3-phase only, 6-16A)
- VW ID.3 (3-phase charging only)
- Enphase solar system with battery
- Home Assistant on Ubuntu (Snap install)
- All on same WiFi network

**Status:** ✅ Setup komplett abgeschlossen und optimiert (16.05.2026)

### Konfiguration
- HA IP: `192.168.178.37` (Port 8123)
- Wallbox: `192.168.178.102` (Vestel EVC04, OCPP-ID: `vestel_ev`)
- Enphase Envoy: `192.168.178.121`
- OCPP Central System: `ws://192.168.178.37:9000` (SSL deaktiviert)
- HA API Token vorhanden für Remote-Steuerung

### OCPP Integration
- lbbrhzn/ocpp v0.8.0 manuell installiert (custom_components/ocpp/)
- ocpp-lib (v16/v201) in custom_components/ocpp/lib_ocpp/ gebündelt
- Wallbox Firmware: v3.131.0-1.0.138.0

### Automatisierungen (3 Stück, dynamisches Überschussladen)
1. **DL - Strom dynamisch anpassen** — Läuft in 60s-Schleife, regelt Ampere basierend auf PV-Überschuss (6-16A, 3-phasig, 690V)
2. **DL - Start bei Solarüberschuss** — Startet bei ≥4,0 kW Export für 2 Minuten
3. **DL - Stop bei wenig Sonne** — Stoppt bei <0,5 kW Export für 5 Minuten

Wichtige Entities:
- `sensor.envoy_122323101510_aktueller_nettostromverbrauch` — negativ = Export, positiv = Import
- `switch.vestel_ev_charge_control` — on/off
- `number.vestel_ev_maximum_current` — 6-16A (min auf 6 geändert)

### Template-Sensoren (configuration.yaml)
- `sensor.envoy_batterieleistung` — Batterieleistung berechnet (kW)
- `sensor.netzimport_leistung` / `sensor.netzeinspeisung_leistung` — getrennte Im/Export (kW)
- `sensor.batterieladung_leistung` / `sensor.batterieentladung_leistung` — getrennte Batterieflüsse (kW)
- Riemann-Summen: `produktion_heute`, `verbrauch_heute`, `netzimport_heute`, `netzeinspeisung_heute`, `batterieladung_heute`, `batterieentladung_heute`, `wallbox_heute` (kWh)
- Utility Meter (daily reset): `produktion_tag`, `verbrauch_tag`, etc.
- `sensor.pv_uberschuss` — aktueller PV-Export in kW
- `sensor.berechneter_zielstrom` — was die Automation berechnen würde (A)
- `sensor.algorithmus_phase` — aktueller Status (🔌/⏳/⚡)
- `sensor.fahrzeug_status` — Connector Status auf Deutsch

### Dashboard "PV & Wallbox" (url_path: pv-wb)
- Kachel "PV-Anlage aktuell": Live-Produktion, Verbrauch, Netzbezug, Batteriebezug, Batterie%
- Kachel "PV-Anlage heute": Bezug (Netz/PV/Batterie), Export (Netz/Wallbox/Batterie), Gesamt (Netz/Verbrauch) in kWh
- Kachel "Wallbox": Ladung, Max Strom, Ladeleistung, Fahrzeugstatus
- Kachel "Überschussladen": PV-Überschuss, Zielstrom, Ist-Strom, Ladeleistung, Algorithmus-Phase
- ApexCharts-Card installiert (www/), aber wegen Konfigurationsfehler deaktiviert

### Dateizugriff & Sync
- `automations.yaml`, `configuration.yaml` — direkt beschreibbar nach `/var/snap/home-assistant-snap/695/`
- `.storage/lovelace.entw_algo` — root-owned, nur via systemd-run kopierbar
- **⚠️ Systemd Path Watcher aktiv:** `sync-ha-config.path` überwacht Workspace-Dateien und kopiert automatisch ins Snap-Verzeichnis bei Änderung
- **⚠️ Nach JEDER Änderung: HA neustarten!** → `systemctl restart snap.home-assistant-snap.home-assistant-snap.service`
  (dann poll bis HTTP 200)
- Workspace → Snap: automatisch via Path Watcher (nach Dateisave)
- Snap → Workspace: muss manuell gemacht werden (hier arbeiten wir im Workspace)

## About Wolfgang
- Timezone: Europe/Berlin (UTC+1/+2)
- Pronouns: it/its
- Focus: Practical Home Assistant automation
- Patient, methodical approach to setup

## About OpenClaw (me)
- Direct, resourceful, no fluff
- Honest and casual communication
- Gets things done
- Emoji: 🐾
- **Update-Instruktion:** Sobald ein Update für mich verfügbar ist, installieren (eingetragen 05.06.2026)
