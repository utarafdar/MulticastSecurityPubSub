from Crypto.Cipher import AES
from Crypto import Random
import os
import base64
import json

def encrypt_aes(key, message):
    iv = Random.new().read(AES.block_size)
    enc_suite = AES.new(key, AES.MODE_CFB, iv)
    return iv + enc_suite.encrypt(message)


def decrypt_aes(key, enc_message):
    # enc_message = base64.b64decode(enc_message)
    iv = enc_message[:AES.block_size]
    enc_suite = AES.new(key, AES.MODE_CFB, iv)
    return enc_suite.decrypt(enc_message[AES.block_size:])


key1 = os.urandom(16)
"""enc = encrypt_aes(key1, "this is  message to be encrypted")
print(enc)
print(decrypt_aes(key1, enc))
key1 = os.urandom(16)
string = key1.decode("utf-8", "ignore")
hex = key1.hex()
print(key1)
print (key1.hex())
print(bytes.fromhex(hex))"""
