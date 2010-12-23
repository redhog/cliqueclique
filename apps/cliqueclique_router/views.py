import fcdjangoutils.jsonview
import security_context

@fcdjangoutils.jsonview.json_view
def create_security_context(request):
    assert parent_key is not None
    return security_context.create_security_context(request, request.POST['parent_key'])

@fcdjangoutils.jsonview.json_view
def delete_security_context(request, key, delete_key):
    assert delete_key is not None
    return security_context.delete_security_context(request, request.POST['key'], request.POST['delete_key'])

@fcdjangoutils.jsonview.json_view
def get_security_context(request, key):
    assert key is not None
    return security_context.get_security_context(request, key)
