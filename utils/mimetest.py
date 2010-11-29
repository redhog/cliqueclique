import email
import email.generator
import email.mime.message
import email.mime.application
import email.mime.text
import email.mime.multipart
import email.header
import email.feedparser

import utils.smime

signer_cert, signer_key =  utils.smime.make_self_signed_cert("kafoo", 1024)
signer_cert = utils.smime.der2pem(signer_cert)
signer_key = utils.smime.der2pem(signer_key, "PRIVATE KEY")

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
