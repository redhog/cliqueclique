import django.shortcuts
import django.template
import django.core.urlresolvers
import cliqueclique_document.models
import cliqueclique_subscription.models
import email.mime.text

def display(request, document_id):
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
