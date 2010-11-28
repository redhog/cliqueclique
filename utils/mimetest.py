import email
import email.generator
import email.mime.message
import email.mime.application
import email.mime.text
import email.mime.multipart
import email.header
import email.feedparser

import utils.smime

signer_cert = """-----BEGIN CERTIFICATE-----
MIICsDCCAhmgAwIBAgIJAIdNkd88O6ZOMA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIEwpTb21lLVN0YXRlMSEwHwYDVQQKExhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMTAxMTI2MjMyMDIxWhcNMTAxMjI2MjMyMDIxWjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECBMKU29tZS1TdGF0ZTEhMB8GA1UEChMYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKB
gQDJ+AL8Usi5fih6FITvO+ZGbynk61zcWA+SMhhpCluPjbpkxt0SL6FP6NI3ushl
fh1Yo4DjDh/iwYdknL/mqGqMAlzv3f8YfHFPXLLmCadbjIK49EgJSbKyuhQ0BuaG
hCoc/XbJzrhue1/znSvzf2Eyn9VmlbzCopPuKsGXxMNldwIDAQABo4GnMIGkMB0G
A1UdDgQWBBREa2U9yBXDCwxW6cyG4ZAjfB+TbjB1BgNVHSMEbjBsgBREa2U9yBXD
CwxW6cyG4ZAjfB+TbqFJpEcwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgTClNvbWUt
U3RhdGUxITAfBgNVBAoTGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZIIJAIdNkd88
O6ZOMAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEFBQADgYEAGdZOWb3HKqv1IL2C
vkTWknBLXaxpVk86ad9bpcPG9CJGQaHMmtskDcK8H25n1lZ86rv1CExuqLp4dpge
8SDVPbcSONg6BlS2z6jzvoPYo5WvuSMCxCQqXtkMO9XW3Jo+0+ZROwNE6GbvxncT
pJJ/VLrW0qkZiPEohLD413z5ddM=
-----END CERTIFICATE-----"""

signer_key = """-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQDJ+AL8Usi5fih6FITvO+ZGbynk61zcWA+SMhhpCluPjbpkxt0S
L6FP6NI3ushlfh1Yo4DjDh/iwYdknL/mqGqMAlzv3f8YfHFPXLLmCadbjIK49EgJ
SbKyuhQ0BuaGhCoc/XbJzrhue1/znSvzf2Eyn9VmlbzCopPuKsGXxMNldwIDAQAB
AoGASzzm79RvDhrfPUszkmOADzEOLEc5mqP7ePzMdyTyovGrRCuI42N29mvHFBey
24w1pnWSaAM1AaYSp/p0yppmxgQUb6/mL93B1OdA9RBAm9cysMhu5oPE+NItxobL
0lvx6LEI3jHk+SGsKLrMIwBj1FFNAvkw/l06jYGaLADLdpECQQDmxVdl2PAhomTc
MxVrDVsn1cCvYZOaexmueTJcgQI+wO0+u0WTBz19SsJ4BvAhkfMQ7nbDeuUpa0tJ
6dKPCRldAkEA4AyT1MLGm1dJiKNA6N2Hbmahn7CCyN7sgAiN+vyVcwVwY/jd0NRp
sWBO1LBEOdsG4ZQ+Nf+ZgIf3HpYniRMI4wJBANgi+lFclsOZuod2nNfQAZFUpQxe
AoXMR+hegOmctsKZpVp8wZQMUu33SB5suRln/dTc04UQpHNfl3tZsSjgZ80CQQCN
zYgXJfvbv6Ar2d+wQt1/s3diAa6VAfq/giqSiyDvvqaGr7F8haQrfqAGH1XfJFAz
n8bMGG0IG4X9lt2I9UIvAkEAm/bEffnqcUI5r/tslDaSbmMuPKXfRF6dWcRFGecc
7wR7wIrvK+nXn0hVIblVoeUy5vGeDAmFLyKfMqFlTOFl1w==
-----END RSA PRIVATE KEY-----"""

msg1 = email.mime.multipart.MIMEMultipart()
msg1.add_header("Msg", "msg1")

msg2 = email.mime.text.MIMEText("Blabla")
msg2.add_header("Msg", "msg2")

msg1.attach(msg2)

msg3 = utils.smime.MIMESigned()
msg3.set_private_key(signer_key)
msg3.set_cert(signer_cert)
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

assert ret

print "Everything's OK"
