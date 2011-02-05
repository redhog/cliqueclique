import cliqueclique_document.models
import fcdjangoutils.jsonview
import utils.djangosmime
import cliqueclique_node.models

node = cliqueclique_node.models.LocalNode.objects.get(node_id="1816c00647448633b4040ab2fc6195e4c723681468d1c447df991")

d = {"__cliqueclique_document_models_Document__": True,
     "content": {"__smime_MIMESigned__": True,
                 "header": {},
                 "parts": [{"__email_mime_multipart_MIMEMultipart__": True,
                            "parts": [{"__email_message_Message__": True,
                                       "body": "link1",
                                       "header": {"link_direction": "natural",
                                                  "part_type": "link",
                                                  "Content-Type": "text/plain; charset=\"us-ascii\"",
                                                  "kafoo": "root:sub3"}}],
                            "header": {"child_document_id": "22c49a3f440cefffee5b0183fdbdea365d39a4eebc65d1c4029e4",
                                       "parent_document_id": "74f0b3f760a9a2345302d3af0be756fb2a3a7569e9ebd60f8e1b2",
                                       "name": "link1"}}],
                 }
     }

j = fcdjangoutils.jsonview.to_json(d)
d = fcdjangoutils.jsonview.from_json(j, public_key=utils.smime.der2pem(node.public_key), private_key=utils.smime.der2pem(node.private_key, "PRIVATE KEY"))

print type(d)
print d.document_id
print d.content
