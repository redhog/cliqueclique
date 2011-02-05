import cliqueclique_document.models, cliqueclique_node.models, utils.djangosmime, fcdjangoutils.jsonview
doc = list(cliqueclique_document.models.Document.objects.all())[-1]
node = cliqueclique_node.models.LocalNode.objects.get(node_id="1816c00647448633b4040ab2fc6195e4c723681468d1c447df991")
x = fcdjangoutils.jsonview.from_json(fcdjangoutils.jsonview.to_json(doc.as_mime))
x.set_private_key(utils.smime.der2pem(node.private_key, "PRIVATE KEY"))
x.as_string()
