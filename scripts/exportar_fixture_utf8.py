# -*- coding: utf-8 -*-
import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.core.management import call_command

fixture_path = r'c:\SINETEC\SINETEC\sinetec_fixture_completa.json'
with open(fixture_path, 'w', encoding='utf-8') as f:
    call_command(
        'dumpdata',
        natural_foreign=True,
        natural_primary=True,
        exclude=['contenttypes', 'auth.permission'],
        indent=2,
        stdout=f
    )

print(f"[OK] Fixture exportada con éxito en UTF-8: {fixture_path} ({os.path.getsize(fixture_path)} bytes)")
