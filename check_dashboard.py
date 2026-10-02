import django, os, re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()
from django.test import Client
from django.contrib.auth.models import User

client = Client()
user = User.objects.filter(username='admin').first()
client.force_login(user)
r = client.get('/dashboard/')
html = r.content.decode('utf-8', errors='replace')

# Check Bootstrap JS
print('Bootstrap JS present:', 'bootstrap.bundle.min.js' in html)

# Find all modal divs
modals = re.findall(r'id="(modal[^"]+)"', html)
print('=== MODALS IN PAGE ===')
for m in set(modals):
    print(' -', m)

# Find data-bs-target references
targets = re.findall(r'data-bs-target="([^"]+)"', html)
print('=== MODAL TRIGGER TARGETS ===')
for t in set(targets):
    print(' -', t)

# Check if modals match triggers
print('\n=== MATCHING ANALYSIS ===')
triggers = {t.lstrip('#') for t in targets}
modal_ids = set(modals)
matched = triggers & modal_ids
missing = triggers - modal_ids
print('Matched triggers:', matched)
print('MISSING modals (trigger with no matching modal):', missing)
