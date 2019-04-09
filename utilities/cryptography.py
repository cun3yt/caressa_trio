import hashlib


def compute_hash(txt: str) -> str:
    return hashlib.sha256(txt.encode('utf-8')).hexdigest()
