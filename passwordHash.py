import hashlib
import secrets
import base64

def hash_password(password):
    """
    Hash a password using SHA-256 with a random salt.
    
    Takes in:
        password (str): The password string to hash
        
    Returns:
        str: The hashed password with salt, encoded as base64
    """
    # Generate a random salt
    salt = secrets.token_bytes(32)
    
    # Combine password and salt, then hash
    password_bytes = password.encode('utf-8')
    hash_obj = hashlib.sha256(salt + password_bytes)
    hashed_password = hash_obj.digest()
    
    # Combine salt and hash, then encode as base64 for storage
    combined = salt + hashed_password
    return base64.b64encode(combined).decode('utf-8')

def verify_password(password, hashed_password):
    """
    Verify a password against its hash.
    
    Args:
        password (str): The plain text password to verify
        hashed_password (str): The stored hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        # Decode the stored hash
        combined = base64.b64decode(hashed_password.encode('utf-8'))
        
        # Extract salt (first 32 bytes) and hash (remaining bytes)
        salt = combined[:32]
        stored_hash = combined[32:]
        
        # Hash the provided password with the extracted salt
        password_bytes = password.encode('utf-8')
        hash_obj = hashlib.sha256(salt + password_bytes)
        new_hash = hash_obj.digest()
        
        # Compare hashes
        return new_hash == stored_hash
    except Exception:
        return False
