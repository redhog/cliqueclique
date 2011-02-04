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
    return {'__email_message_Message__': True, 'header': dict(obj), 'body': obj.get_payload()}

@fcdjangoutils.jsonview.JsonDecodeRegistry.register('__email_message_Message__')
def conv(obj):
    res = email.message.Message()
    for key, value in obj['header'].iteritems():
        res[key] = value
    res.set_payload(obj['body'])
    return res

@fcdjangoutils.jsonview.JsonEncodeRegistry.register(email.mime.multipart.MIMEMultipart)
def conv(obj):
    return {'__email_mime_multipart_MIMEMultipart__': True, 'header': dict(obj), 'parts': obj.get_payload()}

@fcdjangoutils.jsonview.JsonDecodeRegistry.register('__email_mime_multipart_MIMEMultipart__')
def conv(obj):
    res = email.mime.multipart.MIMEMultipart()
    for key, value in obj['header'].iteritems():
        res[key] = value
    for part in obj['parts']:
        res.attach(part)
    return res

@fcdjangoutils.jsonview.JsonEncodeRegistry.register(smime.MIMESigned)
def conv(obj):
    cert = obj.verify()[0]
    data = smime.cert_get_data(cert)
    return {'__smime_MIMESigned__': True,
            'header': dict(obj),
            'signature': {'cert': smime.der2pem(cert),
                          'node_id': cliqueclique_node.models.Node.node_id_from_public_key(cert),
                          'name': data['name'],
                          'address': data['address']},
            'parts': [obj.get_payload()[0]]}

@fcdjangoutils.jsonview.JsonDecodeRegistry.register('__smime_MIMESigned__')
def conv(obj):
    res = smime.MIMESigned()
    for key, value in obj['header'].iteritems():
        res[key] = value
    if 'signature' in obj:
        res.set_cert(obj['signature']['cert'])
    res.attach(obj['parts'][0])
    return res
