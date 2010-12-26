import utils.hash

def make_secure_id(server_key, document_id, do_secure = True):
    if not do_secure:
        return document_id
    return document_id + ':' + utils.hash.hash_id_from_data(document_id + ':' + server_key)

def verify_secure_id(server_key, document_id):
    if not ':' in document_id:
        return False, document_id
    document_id, security_key = document_id.split(':')
    if security_key != utils.hash.hash_id_from_data(document_id + ':' + server_key):
        raise Exception("Security key does not match")
    return True, document_id

