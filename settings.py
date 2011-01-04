# Find all locally installed apps
import os.path, sys
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_ROOT, "apps"))
LOCAL_APPS = filter(
    lambda x: os.path.isfile(os.path.join(PROJECT_ROOT, 'apps', x,'__init__.py')), 
    os.listdir(os.path.join(PROJECT_ROOT, 'apps')))

virtualenv = os.path.join(PROJECT_ROOT, "deps/bin/activate_this.py")
if os.path.exists(virtualenv):
    execfile(virtualenv, dict(__file__=virtualenv))

# Django settings for cliqueclique project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'node.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None # Don't set this or OpenSSL cert generation will generate certs in the future! Kapsie?

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'pc#xoc0*z4t^q2231n&*u(w4m$6rs1752hnwczwv3juy8$%-g&'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    "fcdjangoutils.widgettagmiddleware.WidgetTagMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'cliqueclique_router.middleware.ChangeSignalMiddleware',
)

ROOT_URLCONF = 'cliqueclique.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates")
)

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    
    "staticfiles.context_processors.static_url",
    "cliqueclique_ui_security_context.security_context.context_processor",
]

INSTALLED_APPS = [
    'fcdjangoutils',
    'staticfiles',
    'registration',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
]
INSTALLED_APPS.extend(
    LOCAL_APPS
    )

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "media"),
]

STATICFILES_DIRS.extend(
    map(
        lambda x: os.path.join(PROJECT_ROOT,'apps',x,'media'), 
        LOCAL_APPS))

CLIQUECLIQUE_LOCALHOST = True
CLIQUECLIQUE_ADDRESS_LENGTH = 61
CLIQUECLIQUE_HASH_LENGTH = 53 # Same as i2p b32 address length, just for fun :)

CLIQUECLIQUE_HASH_PRINT_LENGTH = 5
CLIQUECLIQUE_KEY_SIZE = 1024

CLIQUECLIQUE_I2P_SESSION_NAME = "cliqueclique"

CLIQUECLIQUE_UI_SECURITY_CONTEXTS = ["localhost:%s" % (8000 + port,) for port in xrange(0, 5)]
