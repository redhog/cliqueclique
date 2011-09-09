# Thanks for ideas to:
# SMIME verification w/o a local cert:
# http://code.activestate.com/recipes/285211-verifying-smime-signed-email-with-m2crypto-and-no-/

import email
import email.generator
import email.mime.multipart
import email.mime.text
import email.header
import email.feedparser

import M2Crypto.BIO
import M2Crypto.Rand
import M2Crypto.SMIME
import M2Crypto.X509

import base64
import difflib
import time
import re

import unittest

def message_from_anything(msg):
    if isinstance(msg, unicode):
        msg = str(msg)
    if isinstance(msg, str):
        msg = email.message_from_string(msg)
    return msg

class VerifierError(Exception): pass
class VerifierContentError(VerifierError): pass

der2pem_linewrapre = re.compile('(' + '.'*64 + ')')

def der2pem(der, type="CERTIFICATE"):
    return "-----BEGIN %s-----\n%s\n-----END %s-----" % (type, der2pem_linewrapre.sub('\\1\n', base64.encodestring(der).replace("\n", "")), type)

def pem2der(pem):
    pem = pem.replace('\r', '')
    return base64.decodestring(
        ("\n" + pem + "\n").split("\n-----BEGIN", 1)[1].split("-----\n", 1)[1].split("\n-----END")[0])

def make_self_signed_cert(name, address, bits=1024):
    pk = M2Crypto.EVP.PKey()
    pk.assign_rsa(M2Crypto.RSA.gen_key(bits, 65537, lambda *args: None))

    cert = M2Crypto.X509.X509()
    cert.set_serial_number(1)
    cert.set_version(2)    

    cert.get_subject().CN = name
    cert.get_issuer().CN = name

    ext = M2Crypto.X509.new_extension('subjectAltName', 'URI:clique://' + address)
    ext.set_critical(0)
    cert.add_ext(ext)

    start = M2Crypto.ASN1.ASN1_UTCTIME()
    start.set_time(long(time.time()) + time.timezone)
    cert.set_not_before(start)
    end = M2Crypto.ASN1.ASN1_UTCTIME()
    # This seems to be MAX possible date in X509, after that it wraps around!?
    end.set_time(60 * 60 * 24 * 365 * 60)
    cert.set_not_after(end)

    cert.set_pubkey(pk)
    cert.sign(pk, 'sha1')

    assert cert.verify(pk)

    # pk.as_der() returns wrong data - maybe public key?
    return cert.as_der(), pem2der(pk.as_pem(None))

def cert_get_data(cert):
    cert_data = M2Crypto.BIO.MemoryBuffer(der2pem(cert))
    cert = M2Crypto.X509.load_cert_bio(cert_data)
    subject = cert.get_subject()
    data = {}
    data['name'] = subject.CN
    data['address'] = cert.get_ext('subjectAltName').get_value()[len('URI:clique://'):]
    return data

_parse_headers = email.feedparser.FeedParser._parse_headers
def parse_headers(self, lines):
    res = _parse_headers(self, lines)
    content_type = self._cur.get_content_type()
    meth = getattr(self, "_get_message_class_" + content_type.replace("/", "_").replace("-", "_"), None)
    if meth is None:
        meth = getattr(self, "_get_message_class_" + content_type.split("/")[0], None)
    if meth is not None:
        cur = self._cur
        self._cur = meth()
        self._msgstack[-1] = self._cur
        if len(self._msgstack) > 1:
            payload = self._msgstack[-2].get_payload()
            payload.remove(cur)
            payload.append(self._cur)
        for key in self._cur.keys():
            del self._cur[key]
        for key, val in cur.items():
            self._cur.add_header(key, val)
    return res
email.feedparser.FeedParser._parse_headers = parse_headers

def get_message_class_multipart(self):
    return email.mime.multipart.MIMEMultipart()
email.feedparser.FeedParser._get_message_class_multipart = get_message_class_multipart

def get_message_class_multipart_signed(self):
    return MIMESigned()
email.feedparser.FeedParser._get_message_class_multipart_signed = get_message_class_multipart_signed

def get_message_class_application_x_pkcs7_mime(self):
    return MIMEEncrypted()
email.feedparser.FeedParser._get_message_class_application_x_pkcs7_mime = get_message_class_application_x_pkcs7_mime


def handle_multipart_signed(self, msg):
    msg._write(self)
email.generator.Generator._handle_multipart_signed = handle_multipart_signed

def handle_multipart_encrypted(self, msg):
    msg._write(self)
email.generator.Generator._handle_multipart_encrypted = handle_multipart_encrypted

# Bugfix: if epiloque is None, no new-line is added at the end of the
# message, but the feedparser reads such a message as having an
# epiloque of '', which then when printed again results in a message
# that ends in a new-line... This makes the thingy idempotent...
# Same thing with an empty payload...
_handle_multipart = email.generator.Generator._handle_multipart
def handle_multipart(self, msg):
    try:
        epilogue = msg.epilogue
        payload = msg.get_payload()
        if msg.epilogue == '':
            msg.epilogue = None
        if payload == []:
            empty = email.mime.text.MIMEText('')
            for key in empty.keys():
                del empty[key]
            msg.set_payload([empty])
        return _handle_multipart(self, msg)
    finally:
        msg.set_payload(payload)
        msg.epilogue = epilogue
email.generator.Generator._handle_multipart = handle_multipart

class MIMEM2(email.mime.multipart.MIMEMultipart):
    def _write_headers(self, gen):
        payload = self.get_payload()
        for h, v in self.items():
            if len(payload) == 1 and h.lower() in ('content-type', 'mime-version'): continue
            print >> gen._fp, '%s:' % h,
            if gen._maxheaderlen == 0:
                # Explicit no-wrapping
                print >> gen._fp, v
            elif isinstance(v, email.header.Header):
                # Header instances know what to do
                print >> gen._fp, v.encode()
            elif email.generator._is8bitstring(v):
                # If we have raw 8bit data in a byte string, we have no idea
                # what the encoding is.  There is no safe way to split this
                # string.  If it's ascii-subset, then we could do a normal
                # ascii split, but if it's multibyte then we could break the
                # string.  There's no way to know so the least harm seems to
                # be to not split the string and risk it being too long.
                print >> gen._fp, v
            else:
                # Header's got lots of smarts, so use it.
                print >> gen._fp, email.header.Header(
                    v, maxlinelen=gen._maxheaderlen,
                    header_name=h, continuation_ws='\t').encode()
        # The blank line that separates headers from body is output by M2Crypto

class MIMESigned(MIMEM2):
    def __init__(self, boundary=None, _subparts=None, **_params):
        MIMEM2.__init__(self, _subtype='signed', boundary=boundary, _subparts=_subparts, **_params)

    def _write(self, gen):
        payload = self.get_payload()
        if len(payload) == 2:
            gen._fp.write("\n") # The blank line between header and data
            gen._handle_multipart(self)
        else:
            assert len(payload) == 1
            # No blank line here, M2Crypto.SMIME.SMIME.write() creates one...

            payload_data = payload[0].as_string()

            s = M2Crypto.SMIME.SMIME()
            s.load_key_bio(M2Crypto.BIO.MemoryBuffer(der2pem(self.private_key, "PRIVATE KEY")), M2Crypto.BIO.MemoryBuffer(der2pem(self.cert)))
            p7 = s.sign(M2Crypto.BIO.MemoryBuffer(payload_data))
            out = M2Crypto.BIO.MemoryBuffer()
            s.write(out, p7, M2Crypto.BIO.MemoryBuffer(payload_data))
            
            gen._fp.write(out.read())

    def set_private_key(self, key):
        self.private_key = key

    def set_cert(self, cert):
        self.cert = cert

    def verify(self):
        """Verify the signatures of the message and returns a list of
        the signing certificates in DER encoded form."""

        payload = self.get_payload()
        if len(payload) == 1:
            assert self.private_key
            assert self.cert
            return [pem2der(self.cert)]

        assert len(payload) == 2
        
        p7, data_bio = M2Crypto.SMIME.smime_load_pkcs7_bio(M2Crypto.BIO.MemoryBuffer(self.as_string()))
        sk3 = p7.get0_signers(M2Crypto.X509.X509_Stack())

        smime = M2Crypto.SMIME.SMIME()
        certstore = M2Crypto.X509.X509_Store()
        for cert in sk3:
            certstore.add_cert(cert)
        smime.set_x509_store(certstore)
        smime.set_x509_stack(sk3)

        try:
            # Sending in data_bio here makes Python segfault due to an
            # NULL python-state pointer in errors.c... Guido Quality Software?
            v = smime.verify(p7)
        except M2Crypto.SMIME.SMIME_Error, e:
            raise VerifierError, "message verification failed: %s" % e

        if data_bio is not None:
            data = data_bio.read()
            if data != v:
                raise VerifierContentError("message verification failed: payload vs SMIME.verify output diff\n%s\n\n--------{Payload}--------\n%s\n--------{end payload}--------" %
                                           ('\n'.join(list(difflib.unified_diff(data.split('\n'), v.split('\n'), n = 1))), data))
        signer_certs = []
        for cert in sk3:
            signer_certs.append(cert.as_der())
        return signer_certs

class MIMEEncrypted(MIMEM2):
    def __init__(self, boundary=None, _subparts=None, **_params):
        MIMEM2.__init__(self, _subtype='encrypted', boundary=boundary, _subparts=_subparts, **_params)

    def _write(self, gen):
        gen._fp.write(self.encrypt(False))

    def set_private_key(self, key):
        self.private_key = key

    def set_cert(self, cert):
        self.cert = cert
        self.add_cert(cert)

    def add_cert(self, cert):
        if not hasattr(self, "certs"):
            self.certs = []
        self.certs.append(cert)

    def encrypt(self, in_place = True):
        """Encrypts the payload"""

        payload = self.get_payload()

        assert len(payload) == 1
        if isinstance(payload[0], (str, unicode)): return
        payload_data = payload[0].as_string()

        s = M2Crypto.SMIME.SMIME()
        sk = M2Crypto.X509.X509_Stack()
        for cert in self.certs:
            sk.push(M2Crypto.X509.load_cert_bio(M2Crypto.BIO.MemoryBuffer(der2pem(cert))))
        s.set_x509_stack(sk)
        # Set cipher: 3-key triple-DES in CBC mode.
        s.set_cipher(M2Crypto.SMIME.Cipher('des_ede3_cbc'))

        p7 = s.encrypt(M2Crypto.BIO.MemoryBuffer(payload_data))

        out = M2Crypto.BIO.MemoryBuffer()
        s.write(out, p7)
        out = out.read()

        if in_place:
            self.set_payload(out)
        return out

    def decrypt(self, in_place = True, cert = None, private_key = None):
        "Decrypts payload"

        payload_data = self.get_payload()

        if not isinstance(payload_data, (str, unicode)): return

        s = M2Crypto.SMIME.SMIME()
        s.load_key_bio(M2Crypto.BIO.MemoryBuffer(der2pem(private_key or self.private_key, "PRIVATE KEY")), M2Crypto.BIO.MemoryBuffer(der2pem(cert or self.cert)))
        # Ok, this is ugly, but it's a workaround around a limitation
        # in M2Crypto; if there are extra (non-encrypted) headers it
        # fails...
        header = """MIME-Version: 1.0
Content-Disposition: attachment; filename="smime.p7m"
Content-Type: application/x-pkcs7-mime; smime-type=enveloped-data; name="smime.p7m"
Content-Transfer-Encoding: base64

"""
        p7, data_bio = M2Crypto.SMIME.smime_load_pkcs7_bio(M2Crypto.BIO.MemoryBuffer(header + payload_data))
        out = s.decrypt(p7)

        out = email.message_from_string(out)

        if in_place:
             self.set_payload([out])
        return out



class Test(unittest.TestCase):
    def setUp(self):
        self.signer_cert, self.signer_key =  make_self_signed_cert("kafoo", "localhost", 1024)

    def test_sign(self):
        msg1 = email.mime.multipart.MIMEMultipart()
        msg1.add_header("Msg", "msg1")

        msg2 = email.mime.text.MIMEText("Blabla")
        msg2.add_header("Msg", "msg2")

        msg1.attach(msg2)

        msg3 = MIMESigned()
        msg3.set_private_key(self.signer_key)
        msg3.set_cert(self.signer_cert)
        msg3.add_header("Msg", "msg3")

        msg4 = email.mime.multipart.MIMEMultipart()
        msg4.add_header("Msg", "msg4")

        msg5 = email.mime.text.MIMEText("Nunani")
        msg5.add_header("Msg", "msg5")

        msg4.attach(msg5)
        msg3.attach(msg4)
        msg1.attach(msg3)

        #print msg1.as_string()

        msgx = email.message_from_string(msg1.as_string())
        #print msgx.as_string()

        msgy = msgx.get_payload()[1]

        msgy.verify()

        msgy.get_payload()[0]['Foo'] = 'Bar'
        ret = True
        try:
            msgy.verify()
            ret = False
        except:
            pass

        self.assertTrue(ret)

    def test_encrypt(self):
        msg1 = email.mime.multipart.MIMEMultipart()
        msg1.add_header("Msg", "msg1")

        msg2 = email.mime.text.MIMEText("Blabla")
        msg2.add_header("Msg", "msg2")

        msg1.attach(msg2)

        msg3 = MIMEEncrypted()
        msg3.set_cert(self.signer_cert)
        msg3.add_header("Msg", "msg3")

        msg3.attach(msg1)

        msgy = msg3.as_string()

        msgx = email.message_from_string(msgy)
        msgx.set_private_key(self.signer_key)
        msgx.set_cert(self.signer_cert)
        msgx.decrypt()

        self.assertEqual(msg1.as_string(), msgx.get_payload()[0].as_string())

if __name__ == "__main__":
    unittest.main()
