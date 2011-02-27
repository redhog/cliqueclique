from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^import$', "cliqueclique_ui_document.views.import_document"),
    (r'^post$', "cliqueclique_ui_document.views.post"),
    (r'^find/(?P<format>[^/]*)$', "cliqueclique_ui_document.views.document"),
    (r'^find/(?P<format>[^/]*)/(?P<document_id>[^/]*)$', "cliqueclique_ui_document.views.document"),
    (r'^(?P<document_id>[^/]*)/set$', "cliqueclique_ui_document.views.set_document_flags"),
)
