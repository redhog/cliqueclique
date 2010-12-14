import django.template
import cliqueclique_subscription.models
import cliqueclique_node.models
import settings

register = django.template.Library()

@register.inclusion_tag("cliqueclique_ui_displaydocument/tag/display_document.html", takes_context=True)
def display_document(context, document_id):
    info = {}
    if 'STATIC_URL' in context:
        info['STATIC_URL'] = context['STATIC_URL']
    info['document_subscription'] = cliqueclique_subscription.models.DocumentSubscription.objects.get(
        node = context['user'].node,
        document__document_id=document_id)
    doc = info['document_subscription'].document.as_mime

    if doc['content-type'] == 'multipart/signed':
        cert = doc.verify()[0]
        doc = doc.get_payload()[0]

        data = utils.smime.cert_get_data(cert)
        info['document_signature'] = cliqueclique_node.models.Node.node_id_from_public_key(cert)
        info['document_signature_name'] = data['name']
        info['document_signature_address'] = data['address']

    info['document'] = doc
    info['document_body'] = doc.get_payload()

    # if not info['document_subscription'].read:
    #     info['document_subscription'].read = True
    #     info['document_subscription'].save()

    return info

@register.filter
def formatid(id):
    if id is None:
        return 'None'
    return id[:settings.CLIQUECLIQUE_HASH_PRINT_LENGTH]

