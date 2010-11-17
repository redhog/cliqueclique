import django.contrib.admin
import cliqueclique_node.models

django.contrib.admin.site.register(cliqueclique_node.models.Node)
django.contrib.admin.site.register(cliqueclique_node.models.LocalNode)
django.contrib.admin.site.register(cliqueclique_node.models.Peer)
