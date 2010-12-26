import settings
import hashlib
import random

def hash_id_from_data(data):
    h = hashlib.sha512()
    h.update(str(data))
    return h.hexdigest()[:settings.CLIQUECLIQUE_HASH_LENGTH]

def rand_id():
    chars = '0123456789abcdef'
    return ''.join(random.choice(chars) for i in range(settings.CLIQUECLIQUE_HASH_LENGTH))
