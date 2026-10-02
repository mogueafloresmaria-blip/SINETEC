import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()
from django.test import Client
from django.contrib.auth.models import User

client = Client()
user = User.objects.filter(username='admin').first()
client.force_login(user)
r = client.get('/dashboard/')
html = r.content.decode('utf-8', errors='replace')

print('Has interactive cards (progress-bar):', 'progress-bar' in html)
print('Has canvas (OLD):', 'chartNivel' in html)
print('Has modal (NEW):', 'modalFichaRapida' in html)
print('Has Ver lista de 10 (NEW):', 'Ver lista de 10' in html)

# Show the Alumnado section
idx = html.find('Alumnado por Nivel Escolar')
print('\nAlumnado section (next 800 chars):')
print(html[idx:idx+800])
