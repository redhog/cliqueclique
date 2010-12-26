from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^post', "cliqueclique_ui.views.post_document"),
    (r'^(?P<document_id>[^/]*)', "cliqueclique_ui.views.display_document"),
    (r'^', "cliqueclique_ui.views.display_document"),
)
