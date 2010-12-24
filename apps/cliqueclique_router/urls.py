from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^security_context/create/(?P<key>[^/]*)(?P<path>/[^/]*)$', "cliqueclique_router.views.load_in_new_security_context"),
    (r'^security_context/create$', "cliqueclique_router.views.create_security_context"),
    (r'^security_context/delete', "cliqueclique_router.views.create_security_context"),
    (r'^security_context/get/(?P<key>[^/]*)', "cliqueclique_router.views.get_security_context"),
)
