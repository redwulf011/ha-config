#!/usr/bin/env python3
"""
Schnäppchen-Datei-Manager.
Liest bestehende schnäppchen.md, entfernt abgelaufene Einträge,
schreibt neue Einträge aus STDIN (JSON) und pflegt die Quellenliste.

Verwendung:
  echo '[{"store":"Lidl","city":"Würzburg","product":"..."}]' | python3 schnaeppchen_update.py
  python3 schnaeppchen_update.py              # nur bereinigen
"""

import json, os, re, sys
from datetime import date, datetime
from pathlib import Path

# XDG Desktop-Verzeichnis ermitteln
_xdg = os.path.expanduser("~/.config/user-dirs.dirs")
if os.path.exists(_xdg):
    with open(_xdg) as f:
        for line in f:
            if line.startswith("XDG_DESKTOP_DIR"):
                _dir = line.split("=", 1)[1].strip().strip('"').replace("$HOME", os.path.expanduser("~"))
                DESKTOP = os.path.join(_dir, "schnäppchen.md")
                break
        else:
            DESKTOP = os.path.expanduser("~/Schreibtisch/schnäppchen.md")
else:
    DESKTOP = os.path.expanduser("~/Schreibtisch/schnäppchen.md")
TODAY = date.today()
TODAY_STR = TODAY.strftime("%d.%m.%Y")

QUELLEN_HEADER = "## 📌 Geprüfte Quellen"
"""Alles ab dieser Zeile wird unverändert erhalten (Source-Bookmarks)."""


# ─── Datei lesen & schreiben ────────────────────────────────────

def split_sections(lines):
    """Splitte die Datei in (deals_teil, quellen_teil).
    quellen_teil = alles ab der Zeile, die QUELLEN_HEADER enthält (inklusive).
    """
    quellen_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith(QUELLEN_HEADER):
            quellen_start = i
            break
    
    if quellen_start is not None:
        return lines[:quellen_start], lines[quellen_start:]
    return lines, []


def parse_entries(lines):
    """Parse deal-entries aus dem deals-Teil. Returns (header, entries,footer)."""
    entry_indices = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('- [') or stripped.startswith('- **['):
            entry_indices.append(i)
    
    if not entry_indices:
        return lines, [], []
    
    header = lines[:entry_indices[0]]
    
    entries = []
    for idx in entry_indices:
        entry_lines = [lines[idx]]
        j = idx + 1
        while j < len(lines):
            stripped = lines[j].strip()
            if stripped == '' or stripped.startswith('  ') or stripped.startswith('> '):
                entry_lines.append(lines[j])
                j += 1
            else:
                break
        entries.append('\n'.join(entry_lines))
    
    last_end = entry_indices[-1] + 1
    while last_end < len(lines):
        stripped = lines[last_end].strip()
        if stripped == '' or stripped.startswith('  ') or stripped.startswith('> '):
            last_end += 1
        else:
            break
    footer = lines[last_end:]
    
    return header, entries, footer


# ─── Verfall prüfen ────────────────────────────────────────────

def is_expired(entry):
    """Check if an entry contains an expired date."""
    dates = re.findall(r'(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})', entry)
    for d, m, y in dates:
        try:
            if date(int(y), int(m), int(d)) < TODAY:
                return True
        except:
            pass
    
    bis_match = re.search(r'bis\s+(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})', entry)
    if bis_match:
        try:
            if date(int(bis_match.group(3)), int(bis_match.group(2)), int(bis_match.group(1))) < TODAY:
                return True
        except:
            pass
    
    range_match = re.search(r'(\d{1,2})\.(\d{1,2})\.\s*-\s*(\d{1,2})\.(\d{1,2})\.(\d{4})', entry)
    if range_match:
        try:
            if date(int(range_match.group(5)), int(range_match.group(4)), int(range_match.group(3))) < TODAY:
                return True
        except:
            pass
    
    return False


def clean_expired(entries):
    kept = []
    removed = 0
    for entry in entries:
        if is_expired(entry):
            removed += 1
        else:
            kept.append(entry)
    return kept, removed


# ─── Quellen verwalten ──────────────────────────────────────────

def extract_sources(quellen_teil):
    """Extrahiere bestehende Quellen-URLs aus dem Quellen-Abschnitt."""
    urls = set()
    for line in quellen_teil:
        for m in re.finditer(r'\((https?://[^)\s]+)\)', line):
            urls.add(m.group(1))
    return urls


def extract_new_sources(items):
    """Extrahiere Quellen (source/url-Felder) aus neuen Deal-Items."""
    urls = set()
    for item in items:
        src = item.get('source', '') or ''
        if src.startswith('http'):
            urls.add(src)
        url = item.get('url', '') or ''
        if url.startswith('http'):
            urls.add(url)
        store = item.get('store', '')
        city = item.get('city', '')
        # Auch die Quell-Page mit aufnehmen
        if src and not src.startswith('http'):
            # relative source → mit Domain ergänzen
            if 'meinprospekt' in src.lower():
                urls.add(f'https://{src}' if not src.startswith('http') else src)
    return urls


def merge_sources(existing_urls, new_urls):
    """Führe neue Quellen mit bestehenden zusammen (nach Priorität)."""
    merged = existing_urls | new_urls
    return merged


def format_quellen_section(sources_set, extra_notes=None):
    """Baue den Quellen-Abschnitt als Liste von Zeilen."""
    lines = [
        "",
        QUELLEN_HEADER,
        "> Diese Quellen werden bei jedem Lauf automatisch geprüft.",
        "> Hier landen URLs, die sich bewährt haben – auch wenn die allgemeine Suche sie nicht findet.",
        "",
    ]
    
    # Sortiere: erst wichtige Aggregatoren, dann lokale, dann spezifische
    priority = []
    for url in sorted(sources_set):
        label = url
        # Versuche einen lesbaren Label zu generieren
        domain_match = re.match(r'https?://(?:www\.)?([^/]+)', url)
        if domain_match:
            domain = domain_match.group(1)
            path = url.split(domain, 1)[1][:60] if len(url.split(domain, 1)) > 1 else ''
            label = f"{domain}{path}"
        lines.append(f"- [ ] [{label}]({url})")
    
    if extra_notes:
        lines.append("")
        lines.extend(extra_notes)
    
    lines.append("")
    return lines


# ─── Einträge formatieren ──────────────────────────────────────

def format_entry(item):
    store = item.get('store', 'Unbekannt')
    city = item.get('city', '')
    product = item.get('product', '')
    price = item.get('price', '')
    url = item.get('url', '')
    typ = item.get('type', 'Angebot')
    validity = item.get('validity', '')
    source = item.get('source', '')
    
    if typ == 'Prospekt':
        line = f"- **[{store}]({source})** in {city} — {product}"
        if validity:
            line += f" ({validity})"
        return line
    
    store_link = f"[{store}]({source})" if source else store
    line = f"- {store_link} in {city} — {product}"
    if price:
        line += f" — **{price}**"
    if validity:
        line += f" ({validity})"
    if url:
        line += f" → [{url[:50]}...]({url})"
    return line


# ─── Hauptfunktion ──────────────────────────────────────────────

def main():
    path = Path(DESKTOP)
    
    # ── Bestehende Datei parsen ────────────────────────────────
    quellen_teil = []
    deals_teil = []
    
    if path.exists():
        lines = path.read_text(encoding='utf-8').split('\n')
        deals_teil, quellen_teil = split_sections(lines)
        print(f"Gelesen: {len(deals_teil)} Deals-Zeilen, Quellen-Abschnitt {'vorhanden' if quellen_teil else 'fehlt'}")
    
    # ── Aus bestehenden Deals entferne abgelaufene ─────────────
    header, old_entries, footer = parse_entries(deals_teil) if deals_teil else ([], [], [])
    clean_old, removed = clean_expired(old_entries)
    if removed:
        print(f"Entfernt: {removed} abgelaufene Einträge")
    
    # ── Neue Einträge aus STDIN lesen ──────────────────────────
    new_entries = []
    raw_items = []
    if not sys.stdin.isatty():
        try:
            raw = sys.stdin.read()
            if raw.strip():
                raw_items = json.loads(raw)
                if isinstance(raw_items, list):
                    new_entries = [format_entry(item) for item in raw_items]
                    print(f"Neu hinzugefügt: {len(new_entries)} Einträge aus JSON")
        except json.JSONDecodeError as e:
            print(f"Warnung: JSON-Fehler in STDIN: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Warnung: Fehler beim Lesen von STDIN: {e}", file=sys.stderr)
    
    # ── Quellenliste aktualisieren ─────────────────────────────
    existing_sources = extract_sources(quellen_teil)
    new_sources = extract_new_sources(raw_items)
    merged_sources = merge_sources(existing_sources, new_sources)
    
    if new_sources - existing_sources:
        print(f"Quellen aktualisiert: +{len(new_sources - existing_sources)} neue URLs")
    
    # ── Merge: alte saubere + neue, dedupliziert ──────────────
    seen = set()
    all_entries = []
    for entry in clean_old + new_entries:
        norm = re.sub(r'\s+', ' ', entry).strip().lower()
        if norm not in seen:
            seen.add(norm)
            all_entries.append(entry)
    
    # ── Header bauen (falls fehlend) ──────────────────────────
    if not header or len(header) < 2:
        header = [
            "# 🏷️ Schnäppchen & Aktionen",
            f"> Stand: {TODAY_STR} (automatisch aktualisiert)",
            f"> Umkreis: 50 km um Waldbrunn (97295)",
            "",
            "---",
        ]
    
    # ── Quellen-Abschnitt bauen ────────────────────────────────
    extra_notes = [
        "> 💡 Neue Quellen werden automatisch hinzugefügt, sobald ein Deal von dort stammt.",
        f"> 🔄 Nächster Check: {TODAY.strftime('%d.%m.%Y')} — alle URLs werden neu abgefragt.",
    ]
    quellen_lines = format_quellen_section(merged_sources, extra_notes)
    
    # ── Footer (nur im Deals-Teil, vor Quellen) ────────────────
    footer = [
        "",
        "---",
        f"*Zuletzt aktualisiert: {TODAY.strftime('%d.%m.%Y um %H:%M')} Uhr*",
        "*Abgelaufene Angebote werden automatisch entfernt.*",
        "",
    ]
    
    # ── Zusammenbauen ──────────────────────────────────────────
    if not all_entries:
        content = "*Derzeit keine aktuellen Angebote gefunden.*"
    else:
        content = '\n'.join(all_entries)
    
    full = (
        '\n'.join(header) + '\n\n' +
        content + '\n' +
        '\n'.join(footer) + '\n' +
        '\n'.join(quellen_lines)
    )
    
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(full, encoding='utf-8')
    
    print(f"✅ Geschrieben: {path}")
    print(f"📄 {len(all_entries)} Einträge ({len(clean_old)} alt, {len(new_entries)} neu)")
    print(f"🔗 {len(merged_sources)} Quellen-URLs gespeichert")


if __name__ == '__main__':
    main()
