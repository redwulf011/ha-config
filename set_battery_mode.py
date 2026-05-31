#!/usr/bin/env python3
"""Set Enphase battery storage mode via direct Envoy API.

Usage: set_battery_mode.py [self-consumption|backup]
"""
import json
import sys
import urllib.request
import ssl

ENVOY_HOST = "192.168.178.121"
TOKEN = "eyJraWQiOiI3ZDEwMDA1ZC03ODk5LTRkMGQtYmNiNC0yNDRmOThlZTE1NmIiLCJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJhdWQiOiIxMjIzMjMxMDE1MTAiLCJpc3MiOiJFbnRyZXoiLCJlbnBoYXNlVXNlciI6Im93bmVyIiwiZXhwIjoxODEwMjI3Mjg4LCJpYXQiOjE3Nzg2OTEyODgsImp0aSI6ImYwNjBhNGZjLTA1YjYtNGY4OC04YmFiLTE5NmYwNTlkNzM0YyIsInVzZXJuYW1lIjoibWFpbEB3b2xmZ2FuZ3JvdGguZGUifQ.jO7OnTRQEy0PRvXQUWVLFPBxTvq5821-rqjgUy6H67k3m4qR-J2r_txG_No17_5rt5-l6k_ftLbDyP1lNmEcFg"

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("self-consumption", "backup"):
        print("Usage: set_battery_mode.py [self-consumption|backup]")
        sys.exit(1)

    mode = sys.argv[1]
    ctx = ssl._create_unverified_context()
    headers = {"Authorization": f"Bearer {TOKEN}"}

    # GET current tariff
    req = urllib.request.Request(
        f"https://{ENVOY_HOST}/admin/lib/tariff",
        headers=headers,
    )
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.load(resp)

    # Change mode
    old_mode = data["tariff"]["storage_settings"]["mode"]
    data["tariff"]["storage_settings"]["mode"] = mode

    # PUT updated tariff
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"https://{ENVOY_HOST}/admin/lib/tariff",
        data=body,
        headers={**headers, "Content-Type": "application/json"},
        method="PUT",
    )
    with urllib.request.urlopen(req, context=ctx) as resp:
        result = json.load(resp)

    new_mode = result.get("tariff", {}).get("storage_settings", {}).get("mode", "?")
    print(f"Battery mode: {old_mode} → {new_mode}")

    if new_mode != mode:
        print(f"ERROR: Expected {mode}, got {new_mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
