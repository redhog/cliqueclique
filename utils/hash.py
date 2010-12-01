import settings
import hashlib

def has_id_from_data(data):
    h = hashlib.sha512()
    h.update(str(data))
    return h.hexdigest()[:settings.CLIQUECLIQUE_HASH_LENGTH]
