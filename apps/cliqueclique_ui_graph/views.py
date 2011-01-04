import pydot
import cliqueclique_document.models
import cliqueclique_subscription.models
import settings
import django.http
import graph
import stat

def split(s):
    if not s:
        return []
    return s.split(",")

def graph_document(request, document_id):
    node_attrs = split(request.GET.get('node', 'center_node_id'))
    peer_attrs = split(request.GET.get('peer', ''))

    g = graph.DocumentGraph(document_id, node_attrs, peer_attrs)
    x = g.create_png()
    return django.http.HttpResponse(x, mimetype="image/png")

def stat_document(request, document_id):
    attr = request.GET.get('attr', 'peer_nrs')
    g = stat.DocumentGraph(document_id, attr)
    x = g.create_png()
    return django.http.HttpResponse(x, mimetype="image/png")
