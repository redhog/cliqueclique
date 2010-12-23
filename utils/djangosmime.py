import smime
import email
import email.message
import email.generator
import email.mime.multipart
import email.mime.text
import email.header
import email.feedparser
import fcdjangoutils.jsonview
import cliqueclique_node.models

@fcdjangoutils.jsonview.JsonEncodeRegistry.register(email.message.Message)
def conv(obj):
    return {'header': dict(obj), 'body': obj.get_payload()}

@fcdjangoutils.jsonview.JsonEncodeRegistry.register(email.mime.multipart.MIMEMultipart)
def conv(obj):
    return {'header': dict(obj), 'parts': obj.get_payload()}

@fcdjangoutils.jsonview.JsonEncodeRegistry.register(smime.MIMESigned)
def conv(obj):
    cert = obj.verify()[0]
    data = smime.cert_get_data(cert)
    return {'header': dict(obj),
            'signature': {'cert': smime.der2pem(cert),
                          'node_id': cliqueclique_node.models.Node.node_id_from_public_key(cert),
                          'name': data['name'],
                          'address': data['address']},
            'parts': [obj.get_payload()[0]]}
