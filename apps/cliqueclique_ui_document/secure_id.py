import utils.hash
import cliqueclique_ui_security_context.security_context

def make_secure_id_from_server_key(server_key, document_id, do_secure = True):
    if not do_secure:
        return document_id
    return document_id + ':' + utils.hash.hash_id_from_data(document_id + ':' + server_key)

def verify_secure_id_with_server_key(server_key, document_id):
    if not ':' in document_id:
        return False, document_id
    document_id, security_key = document_id.split(':')
    if security_key != utils.hash.hash_id_from_data(document_id + ':' + server_key):
        raise Exception("Security key does not match")
    return True, document_id


def make_secure_id(request, document_id, do_secure = True):
    server_key = cliqueclique_ui_security_context.security_context.get_server_key(request)
    return make_secure_id_from_server_key(server_key, document_id, do_secure)

def verify_secure_id(request, document_id):
    server_key = cliqueclique_ui_security_context.security_context.get_server_key(request)
    return verify_secure_id_with_server_key(server_key, document_id)

def security_aware_view(fn):
    def security_aware_view(request, document_id, *arg, **kw):
        is_secure, document_id = verify_secure_id(request, document_id)
        return fn(request, is_secure, document_id, *arg, **kw)
    return security_aware_view

def secure_view(fn):
    @security_aware_view
    def secure_view(request, is_secure, document_id, *arg, **kw):
        if not is_secure:
            raise Exception("Requires secure link")
        return fn(request, document_id, *arg, **kw)
    return secure_view
