from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^(?P<document_id>[^/]*)/graph', "cliqueclique_ui_graph.views.graph_document"),
    (r'^(?P<document_id>[^/]*)/stat', "cliqueclique_ui_graph.views.stat_document"),
)
