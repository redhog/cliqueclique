import fcdjangoutils.jsonview
import security_context
import django.shortcuts

@fcdjangoutils.jsonview.json_view
def create_security_context(request):
    assert parent_key is not None
    return security_context.create_security_context(request, request.POST['parent_key'])

def load_in_new_security_context(request, key, path):
    assert key is not None
    assert path.startswith('/')
    context = security_context.create_security_context(request, key)
    return django.shortcuts.redirect('http://%s%s' % (context['address'], path))

@fcdjangoutils.jsonview.json_view
def delete_security_context(request, key, delete_key):
    assert delete_key is not None
    return security_context.delete_security_context(request, request.POST['key'])

@fcdjangoutils.jsonview.json_view
def get_security_context(request, key):
    assert key is not None
    return security_context.get_security_context(request, key)
