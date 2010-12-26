import fcdjangoutils.jsonview
import security_context
import django.shortcuts
import django.core.urlresolvers

def load_in_new_security_context(request, key, document_id):
    assert key is not None
    context = security_context.create_security_context(request, key, document_id)

    return django.shortcuts.redirect(
        'http://%s%s' % (
            context['address'],
            django.core.urlresolvers.reverse("cliqueclique_ui.views.display_document", kwargs={'document_id': document_id})))

@fcdjangoutils.jsonview.json_view
def delete_security_context(request, key, delete_key):
    assert delete_key is not None
    return security_context.delete_security_context(request, request.POST['key'])

@fcdjangoutils.jsonview.json_view
def get_security_context(request, key):
    assert key is not None
    return security_context.get_security_context(request, key)
