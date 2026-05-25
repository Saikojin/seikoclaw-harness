import sqlite3
import base64
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

class Vault:
    def __init__(self, db_path="openbrain.db"):
        self.db_path = db_path
        self._key = None

    def unlock(self, master_password: str):
        """Derives the encryption key from the master password and a salt from the DB."""
        # If no salt exists, this is a 'first time' setup
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT salt FROM secrets_vault LIMIT 1")
        row = cur.fetchone()
        
        if row:
            salt = base64.b64decode(row[0])
        else:
            # First time initialization
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        self._key = kdf.derive(master_password.encode())
        self._salt = salt
        conn.close()
        return True

    def set_secret(self, key_name: str, value: str):
        if not self._key:
            raise Exception("Vault is locked. Call unlock() first.")
        
        aesgcm = AESGCM(self._key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, value.encode(), None)
        
        # Combine nonce + ciphertext
        encrypted_blob = base64.b64encode(nonce + ciphertext).decode()
        salt_encoded = base64.b64encode(self._salt).decode()
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO secrets_vault (secret_key, encrypted_value, salt)
            VALUES (?, ?, ?)
        """, (key_name, encrypted_blob, salt_encoded))
        conn.commit()
        conn.close()

    def get_secret(self, key_name: str):
        if not self._key:
            raise Exception("Vault is locked. Call unlock() first.")
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT encrypted_value FROM secrets_vault WHERE secret_key = ?", (key_name,))
        row = cur.fetchone()
        conn.close()
        
        if not row:
            return None
            
        blob = base64.b64decode(row[0])
        nonce = blob[:12]
        ciphertext = blob[12:]
        
        aesgcm = AESGCM(self._key)
        try:
            decrypted = aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted.decode()
        except InvalidTag:
            raise Exception("Failed to decrypt secret. Incorrect master password?")

if __name__ == "__main__":
    # Test
    v = Vault("openbrain.db")
    pw = "test_pass"
    v.unlock(pw)
    v.set_secret("OPENAI_KEY", "sk-12345")
    print(f"Decrypted: {v.get_secret('OPENAI_KEY')}")
