from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^create/(?P<key>[^/]*)(?P<path>/[^/]*)$', "cliqueclique_ui_security_context.views.load_in_new_security_context"),
    (r'^create$', "cliqueclique_ui_security_context.views.create_security_context"),
    (r'^delete', "cliqueclique_ui_security_context.views.create_security_context"),
    (r'^get/(?P<key>[^/]*)', "cliqueclique_ui_security_context.views.get_security_context"),
)
