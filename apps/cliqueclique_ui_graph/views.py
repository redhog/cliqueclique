import pydot
import cliqueclique_document.models
import cliqueclique_subscription.models
import settings
import django.http

def color(objs):
    obj_nr = len(objs)
    objs_per_dimension = pow(obj_nr, 1.0/3.0)
    color_incr_per_obj = max(1, int(255.0 / objs_per_dimension))

    color = {'r': 0, 'g': 0, 'b': 0}
    for obj in objs:
        obj['color'] = "#%(r)02x%(g)02x%(b)02x" % color
        color['r'] += color_incr_per_obj
        if color['r'] > 255:
            color['r'] = 0
            color['g'] += color_incr_per_obj
        if color['g'] > 255:
            color['g'] = 0
            color['b'] += color_incr_per_obj
    return objs

class DocumentGraph(object):
    def __init__(self, document_id, node_attrs, peer_attrs):
        self.graph = pydot.Dot("neato")
        self.graph.set_overlap("scale")

        self.node_attrs = node_attrs
        self.peer_attrs = peer_attrs

        self.center_nodes = {}

        self.add_document(document_id)

    def add_document(self, document_id):
        subs = cliqueclique_subscription.models.DocumentSubscription.objects.filter(document__document_id = document_id)
        for sub in subs:
            self.center_nodes[sub.center_node_id] = {}
        color(self.center_nodes.values())
        for sub in subs:
            self.add_subscription(sub)

    def node_label(self, attrs, sub):
        sub = sub.format_to_dict()
        def attr2label(attr):
            return ''.join(p[0] for p in attr.split('_'))
        return '"%s"' % ('\\n'.join("%s=%s" % (attr2label(attr), sub[attr]) for attr in attrs),)

    def add_subscription(self, sub):
        self.graph.add_node(
            pydot.Node('"%s"' % sub.node.node_id,
                       label=self.node_label(self.node_attrs, sub),
                       color=self.center_nodes[sub.center_node_id]['color']))

        for peer_sub in sub.peer_subscriptions.all():
            info = {}
            info['label'] = self.node_label(self.peer_attrs, peer_sub)

            if info['label'] == '""':
                if peer_sub.peer.node_id > peer_sub.local_subscription.node.node_id:
                    continue
                info['arrowhead'] = 'none'
                info['arrowtail'] = 'none'

            self.graph.add_edge(
                pydot.Edge('"%s"' % peer_sub.local_subscription.node.node_id,
                           '"%s"' % peer_sub.peer.node_id,
                           **info))

def graph_document(request, document_id):
    def split(s):
        if not s:
            return []
        return s.split(",")

    node_attrs = split(request.GET.get('node', 'center_node_id'))
    peer_attrs = split(request.GET.get('peer', ''))

    graph = DocumentGraph(document_id, node_attrs, peer_attrs)
    x = graph.graph.create_png()
    return django.http.HttpResponse(x, mimetype="image/png")
