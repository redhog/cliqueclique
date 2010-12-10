import django.template
import cliqueclique_subscription.models
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
    info['body'] = info['document_subscription'].document.as_mime.get_payload()

    # if not info['document_subscription'].read:
    #     info['document_subscription'].read = True
    #     info['document_subscription'].save()

    return info

@register.filter
def formatid(id):
    return id[:settings.CLIQUECLIQUE_HASH_PRINT_LENGTH]
