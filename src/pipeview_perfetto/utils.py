import hashlib

def stable_hash(key: str, modulo: int) -> int:
    h = hashlib.md5(key.encode('utf-8')).digest()
    val = int.from_bytes(h[:4], 'little', signed=False)
    return val % modulo
