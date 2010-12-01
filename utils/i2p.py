import base64
import hashlib
import sys 

def dest2b32(dest):
    raw_dest = base64.b64decode(dest, '-~') 
    hash = hashlib.sha256(raw_dest) 
    base32_hash = base64.b32encode(hash.digest()) 
    return base32_hash.lower().replace('=', '')+'.b32.i2p' 
