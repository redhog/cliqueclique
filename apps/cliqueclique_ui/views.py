import django.shortcuts
import django.template
import django.core.urlresolvers
import cliqueclique_document.models
import cliqueclique_subscription.models
import email.mime.text
import django.http
import utils.smime
import utils.djangosmime
import django.contrib.auth.decorators
import fcdjangoutils.jsonview

@django.contrib.auth.decorators.login_required
def post_document(request):
    doc = email.mime.text.MIMEText(request.POST['body'])
    for hdr in ('subject', 'parent_document_id'):
        if hdr in request.POST:
            doc.add_header(hdr, request.POST[hdr])

    signed = utils.smime.MIMESigned()
    signed.set_private_key(utils.smime.der2pem(request.user.node.private_key, "PRIVATE KEY"))
    signed.set_cert(utils.smime.der2pem(request.user.node.public_key))
    signed.attach(doc)

    doc = cliqueclique_document.models.Document(content=signed.as_string())
    doc.save()
    sub = cliqueclique_subscription.models.DocumentSubscription(
        node = request.user.node,
        document = doc)
    sub.save()
    for parent in sub.parents.all():
        if not parent.local_is_subscribed:
            parent.local_is_subscribed = True
            parent.save()
    return django.shortcuts.redirect("cliqueclique_ui.views.display_document", document_id=doc.document_id)

@django.contrib.auth.decorators.login_required
def display_document(request, document_id = None):
    return django.shortcuts.render_to_response(
        'cliqueclique_ui/display.html',
        {'document_id': document_id,
         'request': request,
         'bookmarks': cliqueclique_subscription.models.DocumentSubscription.objects.filter(
                node = request.user.node,
                bookmarked=True).all()},
        context_instance=django.template.RequestContext(request))
