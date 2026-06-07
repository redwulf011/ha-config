#!/usr/bin/env python3
"""
Schnäppchen-Scraper: Holt aktuelle Prospekt-Angebote aus dem Umkreis Waldbrunn.
Generiert JSON für schnaeppchen_update.py.

Quellen:
  - meinprospekt.de
  - aktionspreis.de (einfacher HTML-Parse, static rendered)
  - kaufda.de
"""

import json, re, sys
from datetime import date, timedelta
from urllib.request import urlopen, Request
from urllib.parse import quote

PLZ = "97295"
REGION = "Waldbrunn"
CITIES = ["Würzburg", "Waldbrunn", "Wertheim"]
TODAY = date.today()

# ─── Prospekt-Quellen (statisch, da diese URLs stabil sind) ──────

PROSPECT_SOURCES = {
    "Lidl": {
        "Würzburg": "https://www.meinprospekt.de/wuerzburg",
        "Waldbrunn": "https://www.meinprospekt.de/waldbrunn",
        "Wertheim": "https://www.meinprospekt.de/wertheim",
    },
    "Penny": {
        "Waldbrunn": "https://www.meinprospekt.de/waldbrunn",
        "Würzburg": "https://www.meinprospekt.de/wuerzburg",
        "Wertheim": "https://www.meinprospekt.de/wertheim",
    },
    "Netto Marken-Discount": {
        "Würzburg": "https://www.kaufda.de/Wuerzburg/aktuelle-Prospekte",
        "Waldbrunn": "https://www.kaufda.de/Waldbrunn-Kr-Wuerzburg/aktuelle-Prospekte",
        "Wertheim": "https://www.kaufda.de/Wertheim/aktuelle-Prospekte",
    },
    "REWE": {
        "Würzburg": "https://www.kaufda.de/Wuerzburg/aktuelle-Prospekte",
        "Wertheim": "https://www.kaufda.de/Wertheim/aktuelle-Prospekte",
    },
    "EDEKA": {
        "Waldbrunn": "https://www.kaufda.de/Waldbrunn-Kr-Wuerzburg",
        "Wertheim": "https://www.meinprospekt.de/wertheim/edekacenter-de",
    },
    "Kaufland": {
        "Würzburg/Waldbrunn/Wertheim": "https://www.kaufda.de/Wuerzburg/aktuelle-Prospekte",
    },
    "OBI": {
        "Würzburg": "https://www.kaufda.de/Wuerzburg/aktuelle-Prospekte",
        "Waldbrunn": "https://www.kaufda.de/Waldbrunn-Kr-Wuerzburg/aktuelle-Prospekte",
        "Wertheim": "https://www.kaufda.de/Wertheim/aktuelle-Prospekte",
    },
    "Rossmann": {
        "Waldbrunn": "https://www.kaufda.de/Waldbrunn-Kr-Wuerzburg/aktuelle-Prospekte",
    },
    "Müller": {
        "Wertheim": "https://www.kaufda.de/Wertheim/aktuelle-Prospekte",
    },
    "Action": {
        "Würzburg": "https://www.kaufda.de/Wuerzburg/aktuelle-Prospekte",
    },
    "Fressnapf": {
        "Waldbrunn/Wertheim": "https://www.kaufda.de/Waldbrunn-Kr-Wuerzburg/aktuelle-Prospekte",
    },
    "AWG": {
        "Waldbrunn": "https://www.kaufda.de/Waldbrunn-Kr-Wuerzburg/aktuelle-Prospekte",
    },
    "IKEA": {
        "Wertheim": "https://www.kaufda.de/Wertheim/aktuelle-Prospekte",
    },
    "Expert": {
        "Waldbrunn/Würzburg": "https://www.meinprospekt.de/waldbrunn",
    },
    "Globus-Baumarkt": {
        "Würzburg": "https://www.meinprospekt.de/wuerzburg",
    },
    "mömax": {
        "Würzburg": "https://www.meinprospekt.de/wuerzburg",
    },
    "XXXLutz Möbelhäuser": {
        "Wertheim": "https://www.kaufda.de/Wertheim/aktuelle-Prospekte",
    },
    "Getränke Fritze": {
        "Höchberg": "https://www.getraenke-fritze.de/angebote",
    },
}

# ─── Kalenderwoche berechnen ──────────────────────────────────────

def kw(d):
    """ISO-Kalenderwoche."""
    return d.isocalendar()[1]


# ─── Prospekt-Einträge generieren ────────────────────────────────

def generate_prospect_entries():
    """Generiere die Prospekt-Liste für die aktuelle Woche."""
    week_number = kw(TODAY)
    monday = TODAY - timedelta(days=TODAY.weekday())
    sunday = monday + timedelta(days=6)
    
    fmt_mo = monday.strftime("%d.%m.")
    fmt_so = sunday.strftime("%d.%m.")
    fmt_mo_full = monday.strftime("%d.%m.%Y")
    fmt_so_full = sunday.strftime("%d.%m.%Y")
    
    now_year = TODAY.year
    next_monday = monday + timedelta(days=7)
    next_sunday = next_monday + timedelta(days=6)
    fmt_next_mo = next_monday.strftime("%d.%m.")
    fmt_next_so = next_sunday.strftime("%d.%m.")
    fmt_next_mo_full = next_monday.strftime("%d.%m.%Y")
    fmt_next_so_full = next_sunday.strftime("%d.%m.%Y")
    
    items = []
    
    # Samstag = letzter Tag der Woche für viele Prospekte
    saturday = monday + timedelta(days=5)
    fmt_sa = saturday.strftime("%d.%m.%Y")
    
    for store, cities in PROSPECT_SOURCES.items():
        for city, url in cities.items():
            item = {
                "store": store,
                "city": city,
                "product": f"Aktuelle Woche ({fmt_mo}–{fmt_so})",
                "validity": f"bis {fmt_so_full}",
                "type": "Prospekt",
                "source": url,
            }
            items.append(item)
            
            # Nächste Woche für Lidl
            if store == "Lidl" and city == "Würzburg":
                item_next = {
                    "store": store,
                    "city": city,
                    "product": f"Nächste Woche ({fmt_next_mo}–{fmt_next_so})",
                    "validity": f"{fmt_next_mo_full}–{fmt_next_so_full}",
                    "type": "Prospekt",
                    "source": url,
                }
                items.append(item_next)
    
    return items


# ─── Einfaches Scraping von aktionspreis.de ─────────────────────

def fetch_offers_from_aktionspreis(city="wuerzburg"):
    """Versuche, aktuelle Angebote von aktionspreis.de zu holen."""
    url = f"https://www.aktionspreis.de/angebote/{city}"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    items = []
    
    try:
        with urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        
        # Suche nach Angebots-Blöcken
        # aktionspreis.de nutzt klassen wie ap-haendler-angebote
        blocks = re.findall(
            r'<article[^>]*class="[^"]*(?:angebot|offer)[^"]*"[^>]*>.*?</article>',
            html, re.DOTALL
        )
        
        for block in blocks[:20]:  # max 20
            store_match = re.search(r'<span[^>]*class="[^"]*haendler[^"]*"[^>]*>(.*?)</span>', block, re.DOTALL)
            product_match = re.search(r'<span[^>]*class="[^"]*produkt[^"]*"[^>]*>(.*?)</span>', block, re.DOTALL)
            price_match = re.search(r'<span[^>]*class="[^"]*preis[^"]*"[^>]*>(.*?)</span>', block, re.DOTALL)
            
            store = store_match.group(1).strip() if store_match else "Unbekannt"
            product = product_match.group(1).strip() if product_match else ""
            price_raw = price_match.group(1).strip() if price_match else ""
            price = re.sub(r'<[^>]+>', '', price_raw).strip()
            
            if product and price:
                items.append({
                    "store": store,
                    "city": city.capitalize(),
                    "product": product,
                    "price": price,
                    "source": url,
                })
    except Exception as e:
        print(f"  ⚠️ aktionspreis.de ({city}): {e}", file=sys.stderr)
    
    return items


# ─── Hauptfunktion ──────────────────────────────────────────────

def main():
    items = []
    
    # 1. Prospekt-Links generieren
    print("📋 Generiere Prospekt-Einträge…", file=sys.stderr)
    items.extend(generate_prospect_entries())
    print(f"   → {len(generate_prospect_entries())} Prospekt-Einträge", file=sys.stderr)
    
    # 2. Angebote scrapen
    print("🔍 Scrape Angebote…", file=sys.stderr)
    scraped = []
    scraped.extend(fetch_offers_from_aktionspreis("wuerzburg"))
    scraped.extend(fetch_offers_from_aktionspreis("waldbrunn"))
    
    if scraped:
        items.extend(scraped[:30])
        print(f"   → {len(scraped)} gescrapte Angebote", file=sys.stderr)
    else:
        print("   → keine gescrapten Angebote (Quellen ggf. JS-lastig)", file=sys.stderr)
    
    # 3. Als JSON ausgeben
    print("\n💾 JSON an STDOUT:", file=sys.stderr)
    json.dump(items, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
