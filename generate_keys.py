import os
from eth_keys import keys
from eth_account import Account

# Generate random bytes
random_bytes = os.urandom(32)

# Create a private key from random bytes
private_key = keys.PrivateKey(random_bytes)

# Derive the corresponding public key
public_key = private_key.public_key

print("Private Key:", private_key.to_hex())
print("Public Key:", public_key.to_hex())


print((Account.from_key(private_key)).address)

