#!/usr/bin/env python
import os.path

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

virtualenv = os.path.join(PROJECT_ROOT, "deps/bin/activate_this.py")
if os.path.exists(virtualenv):
    execfile(virtualenv, dict(__file__=virtualenv))

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
