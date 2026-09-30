"""
IHC - Practical Approach to Cyber Security
Modular Assignment 2: Basics of Cryptography

Student: Nitesh Vishwakarma

This practical demonstrates:
1. AES symmetric encryption/decryption
2. RSA asymmetric encryption/decryption
3. SHA-256 hashing for integrity
4. RSA-PSS digital signature and verification

Install:
    pip install cryptography
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def symmetric_encryption_demo(message: str):
    # AES-GCM provides confidentiality and integrity for the message.
    key = AESGCM.generate_key(bit_length=256)
    aes = AESGCM(key)
    nonce = os.urandom(12)

    ciphertext = aes.encrypt(nonce, message.encode(), None)
    plaintext = aes.decrypt(nonce, ciphertext, None).decode()

    return key, nonce, ciphertext, plaintext


def rsa_demo(message: str):
    # RSA is used here to demonstrate asymmetric encryption.
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    ciphertext = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    ).decode()

    return private_key, public_key, ciphertext, plaintext


def sha256_demo(message: str):
    digest = hashlib.sha256(message.encode()).hexdigest()
    return digest


def signature_demo(message: str):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    public_key.verify(
        signature,
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    return signature, "Signature verified successfully."


if __name__ == "__main__":
    import os

    message = "Healthcare appointment confirmation: APPT-2026-001"

    print("=" * 60)
    print("BASICS OF CRYPTOGRAPHY - PRACTICAL DEMONSTRATION")
    print("=" * 60)
    print("Input message:", message)

    # 1. Symmetric encryption
    key, nonce, ciphertext, decrypted = symmetric_encryption_demo(message)
    print("\n[1] AES-256-GCM")
    print("Encrypted data:", base64.b64encode(ciphertext).decode())
    print("Decrypted data:", decrypted)
    print("Result: Encryption/decryption successful")

    # 2. Asymmetric encryption
    private_key, public_key, rsa_ciphertext, rsa_plaintext = rsa_demo(message)
    print("\n[2] RSA-2048 OAEP")
    print("Encrypted data:", base64.b64encode(rsa_ciphertext).decode())
    print("Decrypted data:", rsa_plaintext)
    print("Result: Encryption/decryption successful")

    # 3. Hash
    digest = sha256_demo(message)
    print("\n[3] SHA-256")
    print("Message hash:", digest)
    print("Result: Hash generated successfully")

    # 4. Digital signature
    signature, result = signature_demo(message)
    print("\n[4] RSA-PSS Digital Signature")
    print("Signature:", base64.b64encode(signature).decode())
    print("Verification:", result)

    # Integrity check example
    modified_message = message + " - modified"
    modified_digest = sha256_demo(modified_message)
    print("\n[5] Integrity check")
    print("Original hash:", digest)
    print("Modified hash:", modified_digest)
    print("Hashes match:", digest == modified_digest)
    print("Observation: changing the message changes the hash.")
