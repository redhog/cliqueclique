from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^ui', "cliqueclique_ui.views.ui"),
    (r'^ui-post', "cliqueclique_ui.views.post_document"),
    (r'^(?P<document_id>[^/]*)', "cliqueclique_ui.views.display_document"),
    (r'^', "cliqueclique_ui.views.display_document"),
)
