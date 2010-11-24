from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^(?P<document_id>[^/]*)', "cliqueclique_displaydocument.views.display"),
)
