from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Generate signing (ECDSA) key
signing_private_key = ec.generate_private_key(ec.SECP256R1())
signing_public_key = signing_private_key.public_key()

# Generate encryption (ECDH) key
encryption_private_key = ec.generate_private_key(ec.SECP256R1())
encryption_public_key = encryption_private_key.public_key()

# Save keys
def save_key(key, filename, is_private=True):
    with open(filename, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ) if is_private else key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

save_key(signing_private_key, "signing_private.pem", True)
save_key(signing_public_key, "signing_public.pem", False)
save_key(encryption_private_key, "encryption_private.pem", True)
save_key(encryption_public_key, "encryption_public.pem", False)

print("🔑 Keys generated successfully!")
