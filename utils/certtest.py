import utils.smime

cert, pk = utils.smime.make_self_signed_cert("RedHog.ORG", 1024)
print utils.smime.der2pem(cert)
