# Example code for SMIME verification w/o a local cert:
# http://code.activestate.com/recipes/285211-verifying-smime-signed-email-with-m2crypto-and-no-/

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


class Test(unittest.TestCase):
    def setUp(self):
        self.signer_cert, self.signer_key =  make_self_signed_cert("kafoo", "localhost", 1024)

    def sign(self, data):
        s = M2Crypto.SMIME.SMIME()
        s.load_key_bio(M2Crypto.BIO.MemoryBuffer(der2pem(self.signer_key, "PRIVATE KEY")), M2Crypto.BIO.MemoryBuffer(der2pem(self.signer_cert)))
        p7 = s.sign(M2Crypto.BIO.MemoryBuffer(data))
        out = M2Crypto.BIO.MemoryBuffer()
        s.write(out, p7, M2Crypto.BIO.MemoryBuffer(data))
        return out.read()

    def verify(self, data):
        
        p7, data_bio = M2Crypto.SMIME.smime_load_pkcs7_bio(M2Crypto.BIO.MemoryBuffer(data))
        sk3 = p7.get0_signers(M2Crypto.X509.X509_Stack())

        smime = M2Crypto.SMIME.SMIME()
        certstore = M2Crypto.X509.X509_Store()
        for cert in sk3:
            certstore.add_cert(cert)
        smime.set_x509_store(certstore)
        smime.set_x509_stack(sk3)

        # Sending in data_bio here makes Python segfault due to an
        # NULL python-state pointer in errors.c... Guido Quality Software?
        bin_data = smime.verify(p7)
        
        if data_bio is not None:
            inner_data = data_bio.read()
            if inner_data != bin_data:
                raise VerifierContentError("message verification failed: payload vs SMIME.verify output diff\n%s\n\n--------{Payload}--------\n%s\n--------{end payload}--------" %
                                           ('\n'.join(list(difflib.unified_diff(inner_data.split('\n'), bin_data.split('\n'), n = 1))), inner_data))
        signer_certs = []
        for cert in sk3:
            signer_certs.append(cert.as_der())
        return signer_certs


    def test_souble_sign(self):
        self.verify(self.sign(self.sign("""Content-Type: text/plain; charset="utf-8"

Some content
""")))

if __name__ == "__main__":
    unittest.main()
