#!/bin/sh
WORKSPACE=/home/w/.openclaw/workspace
SNAP=/var/snap/home-assistant-snap/695

cp "$WORKSPACE/automations.yaml" "$SNAP/automations.yaml"
cp "$WORKSPACE/configuration.yaml" "$SNAP/configuration.yaml"
cp "$WORKSPACE/lovelace.entw_algo" "$SNAP/.storage/lovelace.entw_algo"
chown root:root "$SNAP/.storage/lovelace.entw_algo"
