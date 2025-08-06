"""
WSGI config for smartbookmarks project.

It exposes the WSGI callable as a module-level variable named
``application``.  This file was generated for this self-contained
project and should work with any WSGI-compliant web server.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartbookmarks.settings')

application = get_wsgi_application()