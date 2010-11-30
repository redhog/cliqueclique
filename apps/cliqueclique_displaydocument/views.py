import django.shortcuts
import django.template
import django.core.urlresolvers
import cliqueclique_document.models
import cliqueclique_subscription.models
import email.mime.text
import django.http
import utils.smime

def display(request, document_id):
    if 'import' in request.POST:
        msg = request.FILES['file'].read()
        request.user.node.receive(msg)
        msg = utils.smime.message_from_anything(msg)
        container_msg = msg.get_payload()[0]
        update_msg = container_msg.get_payload()[0]
        return django.shortcuts.redirect("cliqueclique_displaydocument.views.display", document_id=update_msg['document_id'])

    if 'post' in request.POST:
        doc = email.mime.text.MIMEText(request.POST['body'])
        doc.add_header("Subject", request.POST['subject'])
        doc.add_header("parent_document_id", document_id)
        doc = cliqueclique_document.models.Document(content=doc.as_string())
        doc.save()
        sub = cliqueclique_subscription.models.DocumentSubscription(
            node = request.user.node,
            document = doc)
        sub.save()

    info = {}
    info['document_subscription'] = cliqueclique_subscription.models.DocumentSubscription.objects.get(
        node = request.user.node,
        document__document_id=document_id)

    info['body'] = info['document_subscription'].document.as_mime.get_payload()

    return django.shortcuts.render_to_response('cliqueclique_displaydocument/display.html', info, context_instance=django.template.RequestContext(request))

def download(request, document_id):
    doc = cliqueclique_subscription.models.DocumentSubscription.objects.get(
        node = request.user.node,
        document__document_id=document_id)
    return django.http.HttpResponse(doc.export().as_string(), mimetype="text/plain")
