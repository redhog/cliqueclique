from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^import$', "cliqueclique_ui_document.views.import_document"),
    (r'^(?P<document_id>[^/]*)/set$', "cliqueclique_ui_document.views.set_document_flags"),
    (r'^(?P<document_id>[^/]*)/download$', "cliqueclique_ui_document.views.document_as_mime"),
    (r'^(?P<document_id>[^/]*)/json$', "cliqueclique_ui_document.views.document_as_json"),
    (r'^(?P<document_id>[^/]*)/obtain_secure_access$', "cliqueclique_ui_document.views.obtain_secure_access"),
)
