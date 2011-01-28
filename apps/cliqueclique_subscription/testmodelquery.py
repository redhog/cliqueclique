import cliqueclique_subscription.query
import cliqueclique_document.models
import cliqueclique_subscription.models
import cliqueclique_node.models
import utils.smime
import email.mime.multipart
import email.mime.text

def post(node, content='', parent=None, child=None, content_headers={}, child_headers={}, parent_headers={}):
    msg = email.mime.multipart.MIMEMultipart()

    doc = email.mime.text.MIMEText(content)
    doc.add_header('part_type', 'content')
    for key, value in content_headers.iteritems():
        doc.add_header(key, value)
    msg.attach(doc)

    if parent_headers:
        doc = email.mime.text.MIMEText('')
        doc.add_header('part_type', 'parent_link')
        for key, value in parent_headers.iteritems():
            doc.add_header(key, value)
        msg.attach(doc)
    if child_headers:
        doc = email.mime.text.MIMEText('')
        doc.add_header('part_type', 'child_link')
        for key, value in child_headers.iteritems():
            doc.add_header(key, value)
        msg.attach(doc)
    
    if parent:
        msg.add_header('parent_document_id', parent.document.document_id)
    if child:
        msg.add_header('child_document_id', child.document.document_id)

    signed = utils.smime.MIMESigned()
    signed.set_private_key(utils.smime.der2pem(node.private_key, "PRIVATE KEY"))
    signed.set_cert(utils.smime.der2pem(node.public_key))
    signed.attach(doc)

    doc = cliqueclique_document.models.Document(content=signed.as_string())
    doc.save()
    sub = cliqueclique_subscription.models.DocumentSubscription(
        node = node,
        document = doc,
        local_is_subscribed = True,
        bookmarked = True)
    sub.save()
    return sub

node = cliqueclique_node.models.LocalNode.objects.all()[0]

sub1 = post(node, "sub1")
root = post(node, "root", child=sub1, child_headers={'kafoo': 'root:sub1'})
sub2 = post(node, "sub2", parent=root, parent_headers={'kafoo': 'root:sub2'})
sub3 = post(node, "sub3")
link1 = post(node, "link1", parent=root, child=sub3, content_headers={'kafoo':'root:sub3'})

q = '["|/", ["->", ["=", "kafoo", "root:sub1"]]]'
q = '["->"]'

#print cliqueclique_subscription.query.Query(q).compile().compile()

print list(cliqueclique_subscription.models.DocumentSubscription.get_by_query(q)) #, node.node_id, root.document.document_id))
