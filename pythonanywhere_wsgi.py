"""Sample PythonAnywhere WSGI file.

Copy this file's contents into the WSGI file linked from your PythonAnywhere
Web tab. Replace `yourusername` and the project folder if needed.
"""
import os
import sys


USERNAME = 'yourusername'
PROJECT_DIR = f'/home/{USERNAME}/Smart-University-Management-System'

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.pythonanywhere')
os.environ.setdefault('PYTHONANYWHERE_USERNAME', USERNAME)
os.environ.setdefault('SECRET_KEY', 'replace-this-with-a-long-random-secret-key')

# Optional production values:
# os.environ.setdefault('OPENAI_API_KEY', '')
# os.environ.setdefault('CLOUDINARY_CLOUD_NAME', '')
# os.environ.setdefault('CLOUDINARY_API_KEY', '')
# os.environ.setdefault('CLOUDINARY_API_SECRET', '')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
