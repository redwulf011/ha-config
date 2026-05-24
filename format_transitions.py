with open('/var/snap/home-assistant-snap/695/configuration.yaml') as f:
    conf = f.read()

# Add a blank line before each → in all state sections
import re

# Replace each occurrence of "\n            →" with "\n\n            →"
# This adds a blank line before each arrow
old = conf
conf = conf.replace('\n            →', '\n\n            →')

if old != conf:
    with open('/var/snap/home-assistant-snap/695/configuration.yaml', 'w') as f:
        f.write(conf)
    print('✅ Formatierung aktualisiert: Zeilenumbruch vor jedem →')
else:
    print('⚠️ Keine Änderungen')
