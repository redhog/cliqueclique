import django.shortcuts
import django.template
import django.core.urlresolvers
import cliqueclique_node.models
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

def obtain_secure_access(request, document_id):
    info = {}

    info['secure_document_id'] = secure_id.make_secure_id(request, document_id)
    info['document_document_id'] = document_id
    mime = cliqueclique_document.models.Document.objects.get(document_id = document_id).as_mime
    if isinstance(mime, utils.smime.MIMESigned):
        cert = mime.verify()[0]
        data = utils.smime.cert_get_data(cert)
        info['document_author_name'] = data['name']
        info['document_author_node_id'] = cliqueclique_node.models.Node.node_id_from_public_key(cert)
        info['document_author_address'] = data['address']
        mime = mime.get_payload()[0]
    info['document_subject'] = mime.get('subject', None)

    info['security_context_document_id'] = cliqueclique_ui_security_context.security_context.get_security_context(request)['owner_document_id']
    mime = cliqueclique_document.models.Document.objects.get(document_id =  info['security_context_document_id']).as_mime
    if isinstance(mime, utils.smime.MIMESigned):
        cert = mime.verify()[0]
        data = utils.smime.cert_get_data(cert)
        info['security_context_author_name'] = data['name']
        info['security_context_author_node_id'] = cliqueclique_node.models.Node.node_id_from_public_key(cert)
        info['security_context_author_address'] = data['address']
        mime = mime.get_payload()[0]
    info['security_context_subject'] = mime.get('subject', None)

    return django.shortcuts.render_to_response(
        'cliqueclique_ui_document/obtain_secure_access.html',
        info,
        context_instance=django.template.RequestContext(request))

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
