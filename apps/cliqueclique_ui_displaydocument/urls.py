from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^import', "cliqueclique_displaydocument.views.import_document"),
    (r'^post', "cliqueclique_displaydocument.views.post_document"),
    (r'^(?P<document_id>[^/]*)/set', "cliqueclique_displaydocument.views.set_document_flags"),
    (r'^(?P<document_id>[^/]*)/download', "cliqueclique_displaydocument.views.download_document"),
    (r'^(?P<document_id>[^/]*)', "cliqueclique_displaydocument.views.display_document"),
    (r'^', "cliqueclique_displaydocument.views.display_document"),
)
