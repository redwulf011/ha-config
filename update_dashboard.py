import asyncio, json, websockets

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhZjAwOTNkZjg4ZTI0MWIxYTUzZWQ2NjdkMDNkZDcxYyIsImlhdCI6MTc3ODcxMTUzMywiZXhwIjoyMDk0MDcxNTMzfQ.HG6Fbe_awMh9JzY6Re_AdAUJOBREQ7amssIiJPI-8Mc"

async def main():
    uri = "ws://127.0.0.1:8123/api/websocket"
    async with websockets.connect(uri) as ws:
        await ws.recv()
        await ws.send(json.dumps({"type": "auth", "access_token": TOKEN}))
        await ws.recv()

        mermaid = """flowchart TD
    A["'Aktuell: ${states['sensor.algorithmus_zustand']}'"]
    B["Warten auf<br/>Fahrzeug"]
    C["Warten auf<br/>Sonne"]
    D["Start zahlt"]
    E["'Laden<br/>${states['number.vestel_ev_maximum_current']}A | ${states['sensor.pv_uberschuss']}kW'"]
    F["Stop zahlt"]
    G["Aus"]

    B -- "Stecker drin" --> C
    C -- ">= 1,5kW (${states['sensor.pv_uberschuss']}kW)" --> D
    D -- "30s stabil" --> E
    D -- "< 1,5kW (${states['sensor.pv_uberschuss']}kW)" --> C
    E -- "< 0,3kW (${states['sensor.pv_uberschuss']}kW)" --> F
    F -- "30s stabil" --> G
    F -- "> 0,3kW (${states['sensor.pv_uberschuss']}kW)" --> E
    G -- "Startbereit" --> C

    style A fill:#4CAF50,color:white,stroke:#2E7D32
    style B fill:#e0e0e0,color:#666
    style C fill:#e0e0e0,color:#666
    style D fill:#e0e0e0,color:#666
    style E fill:#e0e0e0,color:#666
    style F fill:#e0e0e0,color:#666
    style G fill:#e0e0e0,color:#666

    ${if(is_state('sensor.algorithmus_zustand', 'Leer'), 'style B fill:#4CAF50,color:white,stroke:#2E7D32,stroke-width:3px', '')}
    ${if(is_state('sensor.algorithmus_zustand', 'WartenSonne'), 'style C fill:#4CAF50,color:white,stroke:#2E7D32,stroke-width:3px', '')}
    ${if(is_state('sensor.algorithmus_zustand', 'StartZaehler'), 'style D fill:#4CAF50,color:white,stroke:#2E7D32,stroke-width:3px', '')}
    ${if(is_state('sensor.algorithmus_zustand', 'Laden'), 'style E fill:#4CAF50,color:white,stroke:#2E7D32,stroke-width:3px', '')}
    ${if(is_state('sensor.algorithmus_zustand', 'StopZaehler'), 'style F fill:#4CAF50,color:white,stroke:#2E7D32,stroke-width:3px', '')}
    ${if(is_state('sensor.algorithmus_zustand', 'Aus'), 'style G fill:#4CAF50,color:white,stroke:#2E7D32,stroke-width:3px', '')}
"""

        config = {
            "views": [{
                "title": "Uebersicht",
                "path": "uebersicht",
                "cards": [
                    {
                        "type": "entities",
                        "title": "PV-Anlage aktuell",
                        "state_color": True,
                        "entities": [
                            {"entity": "sensor.envoy_122323101510_aktuelle_stromproduktion", "name": "Produktion"},
                            {"entity": "sensor.envoy_122323101510_aktueller_stromverbrauch", "name": "Verbrauch"},
                            {"entity": "sensor.envoy_122323101510_aktueller_nettostromverbrauch", "name": "Netzbezug (-Export)"},
                            {"entity": "sensor.envoy_batterieleistung", "name": "Batteriebezug (-Export)"},
                            {"entity": "sensor.envoy_122323101510_batterie", "name": "Batterie", "unit": "%"}
                        ]
                    },
                    {
                        "type": "entities",
                        "title": "PV-Anlage heute",
                        "state_color": True,
                        "entities": [
                            {"type": "section", "label": "Bezug"},
                            {"entity": "sensor.netzimport_heute", "name": "Netz"},
                            {"entity": "sensor.produktion_heute", "name": "PV"},
                            {"entity": "sensor.batterieentladung_heute", "name": "Batterie"},
                            {"type": "section", "label": "Export"},
                            {"entity": "sensor.netzeinspeisung_heute", "name": "Netz"},
                            {"entity": "sensor.wallbox_heute", "name": "Wallbox"},
                            {"entity": "sensor.batterieladung_heute", "name": "Batterie"},
                            {"type": "section", "label": "Gesamt"},
                            {"entity": "sensor.netzimport_heute", "name": "Netz (Bezug)"},
                            {"entity": "sensor.verbrauch_heute", "name": "Verbrauch"}
                        ]
                    },
                    {
                        "type": "entities",
                        "title": "Wallbox",
                        "state_color": True,
                        "entities": [
                            {"entity": "switch.vestel_ev_charge_control", "name": "Ladung"},
                            {"entity": "number.vestel_ev_maximum_current", "name": "Eingestellter Strom"},
                            {"entity": "sensor.vestel_ev_power_active_import", "name": "Ladeleistung"},
                            {"entity": "sensor.fahrzeug_status", "name": "Fahrzeug"}
                        ]
                    },
                    {
                        "type": "entities",
                        "title": "Ueberschussladen",
                        "state_color": True,
                        "entities": [
                            {"entity": "sensor.pv_uberschuss", "name": "PV-Ueberschuss"},
                            {"entity": "sensor.berechneter_zielstrom", "name": "Zielstrom"},
                            {"entity": "number.vestel_ev_maximum_current", "name": "Eingestellter Strom"},
                            {"entity": "sensor.vestel_ev_power_active_import", "name": "Ladeleistung"},
                            {"entity": "sensor.algorithmus_phase", "name": "Phase"},
                            {"entity": "sensor.algorithmus_zustand", "name": "Zustand"},
                            {"entity": "sensor.einstecken_signal", "name": "Signal"}
                        ]
                    },
                    {
                        "type": "custom:mermaid-card",
                        "title": "Algorithmus",
                        "card_size": 9,
                        "content": mermaid
                    }
                ]
            }]
        }

        req = {"id": 1, "type": "lovelace/config/save", "url_path": "pv-wb", "config": config}
        await ws.send(json.dumps(req))
        resp = json.loads(await ws.recv())
        print(f"Config saved: {resp.get('success')}")

asyncio.run(main())
