from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^accounts/', include('registration.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^cliqueclique_ui_security_context/', include('cliqueclique_ui_security_context.urls')),
    (r'', include("staticfiles.urls")),
    (r'', include('cliqueclique_ui_graph.urls')),
    (r'', include('cliqueclique_ui_document.urls')),
    (r'', include('cliqueclique_ui.urls')),
)
