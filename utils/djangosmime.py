import os

# For stand-alone unittest
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

import utils.smime
import email
import email.message
import email.generator
import email.mime.multipart
import email.mime.text
import email.header
import email.feedparser
import fcdjangoutils.jsonview
import cliqueclique_node.models
import unittest

@fcdjangoutils.jsonview.JsonEncodeRegistry.register(email.message.Message)
def conv(self, obj):
    return {'__email_message_Message__': True, 'header': dict(obj), 'body': obj.get_payload()}

@fcdjangoutils.jsonview.JsonDecodeRegistry.register('__email_message_Message__')
def conv(self, obj):
    res = email.message.Message()
    for key, value in obj['header'].iteritems():
        res[key] = value
    res.set_payload(obj['body'])
    return res

@fcdjangoutils.jsonview.JsonEncodeRegistry.register(email.mime.multipart.MIMEMultipart)
def conv(self, obj):
    return {'__email_mime_multipart_MIMEMultipart__': True, 'header': dict(obj), 'parts': obj.get_payload()}

@fcdjangoutils.jsonview.JsonDecodeRegistry.register('__email_mime_multipart_MIMEMultipart__')
def conv(self, obj):
    res = email.mime.multipart.MIMEMultipart()
    for key, value in obj['header'].iteritems():
        res[key] = value
    for part in obj['parts']:
        res.attach(part)
    return res

def cert_to_json(cert):
    data = utils.smime.cert_get_data(cert)
    return {'cert': utils.smime.der2pem(cert),
            'node_id': cliqueclique_node.models.Node.node_id_from_public_key(cert),
            'name': data['name'],
            'address': data['address']}

@fcdjangoutils.jsonview.JsonEncodeRegistry.register(utils.smime.MIMESigned)
def conv(self, obj):
    cert = cert_to_json(obj.verify()[0])
    return {'__smime_MIMESigned__': True,
            'header': dict(obj),
            'signature': cert,
            'parts': [obj.get_payload()[0]]}

@fcdjangoutils.jsonview.JsonDecodeRegistry.register('__smime_MIMESigned__')
def conv(self, obj):
    res = utils.smime.MIMESigned()
    for key, value in obj['header'].iteritems():
        res[key] = value
    if 'signature' in obj and 'cert' in obj['signature']:
        res.set_cert(obj['signature']['cert'])
    elif hasattr(self, 'public_key'):
        res.set_cert(self.public_key)
    if 'signature' in obj and 'private_key' in obj['signature']:
        res.set_private_key(obj['signature']['private_key'])
    elif hasattr(self, 'private_key'):
        res.set_private_key(self.private_key)
    res.attach(obj['parts'][0])
    return res

@fcdjangoutils.jsonview.JsonEncodeRegistry.register(utils.smime.MIMEEncrypted)
def conv(self, obj):
    res = {'__smime_MIMEEncrypted__': True,
           'header': dict(obj)}

    if hasattr(obj, "certs"):
        res['encryption'] = [cert_to_json(utils.smime.pem2der(cert)) for cert in obj.certs],

    cert = None
    private_key = None
    if hasattr(self, "cert") or hasattr(self, "private_key"):
        res['decryption'] = {}

        if hasattr(self, "cert"):
            res['decryption'].update(cert_to_json(utils.smime.pem2der(self.cert)))
            cert = self.cert
        if hasattr(self, "private_key"):
            res['decryption']['private_key'] = self.private_key
            private_key = self.private_key

    try:
        res['parts'] = [obj.decrypt(False, cert, private_key)]
    except:
        res['parts'] = obj.get_payload()

    return res

@fcdjangoutils.jsonview.JsonDecodeRegistry.register('__smime_MIMEEncrypted__')
def conv(self, obj):
    res = utils.smime.MIMEEncrypted()
    for key, value in obj['header'].iteritems():
        res[key] = value

    if 'encryption' in obj:
        for cert in obj['encryption']:
            res.add_cert(cert['cert'])

    if 'decryption' in obj and 'cert' in obj['decryption']:
        res.set_cert(obj['decryption']['cert'])
    elif hasattr(self, 'public_key'):
        res.set_cert(self.public_key)

    if 'decryption' in obj and 'private_key' in obj['decryption']:
        res.set_private_key(obj['decryption']['private_key'])
    elif hasattr(self, 'private_key'):
        res.set_private_key(self.private_key)

    res.attach(obj['parts'][0])
    return res


class Test(unittest.TestCase):
    def setUp(self):
        self.signer_cert, self.signer_key =  utils.smime.make_self_signed_cert("kafoo", "localhost", 1024)
        self.signer_cert = utils.smime.der2pem(self.signer_cert)
        self.signer_key = utils.smime.der2pem(self.signer_key, "PRIVATE KEY")

    def test_sign(self):
        import django.utils.simplejson

        json_data = {"__smime_MIMESigned__": True,
                     "header": {"Msg": "msg2"},
                     "parts": [{"__email_message_Message__": True,
                                "body": "Blabla",
                                "header": {"Msg": "msg1",
                                           "Content-Type": "text/plain; charset=\"us-ascii\""}}]}
        json = django.utils.simplejson.dumps(json_data)
        mime_data = fcdjangoutils.jsonview.from_json(json, public_key = self.signer_cert, private_key = self.signer_key)
        mime = mime_data.as_string()
        mime2 = email.message_from_string(mime)
        json2 = fcdjangoutils.jsonview.to_json(mime2)
        json2_data = django.utils.simplejson.loads(json2)
        self.assertEqual(json2_data['signature']['name'], "kafoo")
        self.assertEqual(json2_data['parts'][0]['header']['Msg'], "msg1")

    def test_encrypt(self):
        import django.utils.simplejson

        json_data = {"__smime_MIMEEncrypted__": True,
                     "header": {"Msg": "msg2"},
                     "encryption": [{"cert": self.signer_cert}],
                     "parts": [{"__email_message_Message__": True,
                                "body": "Blabla",
                                "header": {"Msg": "msg1",
                                           "Content-Type": "text/plain; charset=\"us-ascii\""}}]}
        json = django.utils.simplejson.dumps(json_data)
        mime_data = fcdjangoutils.jsonview.from_json(json, certs = [self.signer_cert])
        mime = mime_data.as_string()


        mime2 = email.message_from_string(mime)
        json2 = fcdjangoutils.jsonview.to_json(mime2, cert = self.signer_cert, private_key = self.signer_key)
        json2_data = django.utils.simplejson.loads(json2)

        self.assertEqual(json2_data['parts'][0]['header']['Msg'], "msg1")
        

if __name__ == "__main__":
    unittest.main()
