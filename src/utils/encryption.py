import base64

def encrypt_password(password: str) -> str:
    """Simple obfuscation for local storage."""
    if not password:
        return ""
    # Simple shift + base64 to avoid clear text
    # This is NOT strong encryption, just obfuscation
    obfuscated = "".join([chr(ord(c) + 1) for c in password])
    return base64.b64encode(obfuscated.encode()).decode()

def decrypt_password(encrypted: str) -> str:
    """Decrypts the obfuscated password."""
    if not encrypted:
        return ""
    try:
        obfuscated = base64.b64decode(encrypted).decode()
        return "".join([chr(ord(c) - 1) for c in obfuscated])
    except:
        return ""
