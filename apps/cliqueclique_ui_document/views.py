import django.shortcuts
import django.template
import django.core.urlresolvers
import cliqueclique_document.models
import cliqueclique_subscription.models
import cliqueclique_ui_security_context.security_context
import email.mime.text
import django.http
import utils.hash
import utils.smime
import utils.djangosmime
import django.contrib.auth.decorators
import fcdjangoutils.jsonview
import secure_id

@django.contrib.auth.decorators.login_required
def import_document(request):
    msg = request.FILES['file'].read()
    request.user.node.receive(msg)
    msg = utils.smime.message_from_anything(msg)
    container_msg = msg.get_payload()[0]
    update_msg = container_msg.get_payload()[0]
    return django.shortcuts.redirect("cliqueclique_ui.views.display_document", document_id=update_msg['document_id'])

@django.contrib.auth.decorators.login_required
def set_document_flags(request, document_id):
    sub = cliqueclique_subscription.models.DocumentSubscription.objects.get(
        node = request.user.node,
        document__document_id = document_id)
    for attr in ('bookmarked', 'read', 'local_is_subscribed'):
        if attr in request.POST:
            attrvalue = request.POST[attr]
        elif attr in request.GET:
            attrvalue = request.GET[attr]
        else:
            continue
        if attrvalue == "toggle":
            value = not getattr(sub, attr)
        elif attrvalue == "true":
            value = True
        else:
            value = False
        setattr(sub, attr, value)
    sub.save()
    return django.shortcuts.redirect("cliqueclique_ui.views.display_document", document_id=sub.document.document_id)

@django.contrib.auth.decorators.login_required
def document_as_mime(request, document_id):
    doc = cliqueclique_subscription.models.DocumentSubscription.objects.get(
        node = request.user.node,
        document__document_id=document_id)
    return django.http.HttpResponse(doc.export().as_string(), mimetype="text/plain")

@fcdjangoutils.jsonview.json_view
@django.contrib.auth.decorators.login_required
@secure_id.security_aware_view
def document_as_json(request, is_secure, document_id = None):
    sub = cliqueclique_subscription.models.DocumentSubscription.objects.get(
        node = request.user.node,
        document__document_id = document_id
        )
    return {
        'document_id': document_id,
        'parents': [parent.document.document_id for parent in sub.parents.all()],
        'children': [secure_id.make_secure_id(request, child.document.document_id, is_secure)
                     for child in sub.children.all()],
        'content': sub.document.as_mime
        }
