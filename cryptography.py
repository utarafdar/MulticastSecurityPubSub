#from Crypto.Cipher import AES
#from Crypto.PublicKey import ECC
#from Crypto import Random
import os
import nacl.secret
import nacl.utils
from nacl.public import PrivateKey, Box
import nacl.encoding
import nacl.signing
from nacl.hash import blake2b
from nacl.encoding import HexEncoder
import base64
import json

"""def encrypt_aes(key, message):
    iv = Random.new().read(AES.block_size)
    enc_suite = AES.new(key, AES.MODE_CFB, iv)
    return iv + enc_suite.encrypt(message)


def decrypt_aes(key, enc_message):
    # enc_message = base64.b64decode(enc_message)
    iv = enc_message[:AES.block_size]
    enc_suite = AES.new(key, AES.MODE_CFB, iv)
    return enc_suite.decrypt(enc_message[AES.block_size:])"""


def encrypt_secret_key(key, message):

    box = nacl.secret.SecretBox(key)
    return box.encrypt(message)


def decrypt_secret_key(key, enc_message):
    box = nacl.secret.SecretBox(key)
    return box.decrypt(enc_message)


def encrypt_public_key(receiver_public_key, sender_private_key, message):
    sender_box = Box(sender_private_key, receiver_public_key)
    return sender_box.encrypt(message)


def decrypt_public_key(sender_public_key, receiver_private_key, enc_message):
    receiver_box = Box(receiver_private_key, sender_public_key)
    return receiver_box.decrypt(enc_message)


def digital_sign_message(signing_key, message):
    signed = signing_key.sign(message)
    verify_key = signing_key.verify_key
    verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)
    return signing_key.sign(message)


def digital_sign_verify(verify_key_hex, signed_message):
    verify_key = nacl.signing.VerifyKey(verify_key_hex,
                                        encoder=nacl.encoding.HexEncoder)
    return verify_key.verify(signed_message)


def add_binary_nums(x, y):
    max_len = max(len(x), len(y))

    x = x.zfill(max_len)
    y = y.zfill(max_len)

    # initialize the result
    result = ''

    # initialize the carry
    carry = 0

    # Traverse the string
    for i in range(max_len - 1, -1, -1):
        r = carry
        r += 1 if x[i] == '1' else 0
        r += 1 if y[i] == '1' else 0
        result = ('1' if r % 2 == 1 else '0') + result
        carry = 0 if r < 2 else 1  # Compute the carry.

    if carry != 0: result = '1' + result

    return result.zfill(max_len)


def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')


#key1 = os.urandom(16)
"""enc = encrypt_aes(key1, "this is  message to be encrypted")
print(enc)
print(decrypt_aes(key1, enc))
key1 = os.urandom(16)
string = key1.decode("utf-8", "ignore")
hex = key1.hex()
print(key1)
print (key1.hex())
print(bytes.fromhex(hex))"""

# testing ecc

#key = ECC.generate(curve='P-256')
#print (key.public_key())
# key = os.urandom(32)
"""key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
print(key)
print(key.hex())
print(type(key.hex()))
print(bytes.fromhex(key.hex()))
enc_data = encrypt_secret_key(key, b"attack at dawn" )
print(enc_data)
print(decrypt_secret_key(key, enc_data))"""

# Generate Bob's private key, which must be kept secret
skbob = PrivateKey.generate()

# Bob's public key can be given to anyone wishing to send
#   Bob an encrypted message
pkbob = skbob.public_key

# Alice does the same and then Alice and Bob exchange public keys
skalice = PrivateKey.generate()
pkalice = skalice.public_key.encode(HexEncoder).decode()


print(type(skalice))
print(type(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE).hex()))
print(pkalice)

# Bob wishes to send Alice an encrypted message so Bob must make a Box with
#   his private key and Alice's public key

# This is our message to send, it must be a bytestring as Box will treat it
#   as just a binary blob of data.
message = b"Kill all humans"
# this here ===
pkalice1 = nacl.public.PublicKey(pkalice, HexEncoder)
enc_message = encrypt_public_key(pkalice1, skbob, message)
print(enc_message)
print(decrypt_public_key(pkbob, skalice, enc_message))


# Generate a new random signing key
"""signing_key1 = nacl.signing.SigningKey.generate()

# Obtain the verify key for a given signing key
verify_key = signing_key1.verify_key

# Serialize the verify key to send it to a third party
verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)

signed = digital_sign_message(signing_key1, b"Kill all humans")
print(signed)
print(digital_sign_verify(verify_key_hex, signed))"""

# test integrity
"""key1 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
print(key1)
print(key2)
enc = encrypt_secret_key(key1, b'testing integrity')
print(decrypt_secret_key(key2, enc))"""

# test mac

msg = b'256 BytesMessage'
msg2 = 16*b'256 bytesMessage'

auth_key = nacl.utils.random(size=64)
# the simplest way to get a cryptographic quality auth_key
# is to generate it with a cryptographic quality
# random number generator

auth1_key = nacl.utils.random(size=64)
# generate a different key, just to show the mac is changed
# both with changing messages and with changing keys

mac0 = blake2b(msg, key=auth_key, encoder=nacl.encoding.HexEncoder)
mac1 = blake2b(msg, key=auth1_key, encoder=nacl.encoding.HexEncoder)
mac2 = blake2b(msg2, key=auth_key, encoder=nacl.encoding.HexEncoder)

print(mac0)
print(mac1)
print(mac2)

listo = list()
list1 = ['a','b']
list2 = ['c', 'd']
listo.extend(list1)
list2.extend(list1)
print(listo)
print(list2)

nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
print(nonce)
print(len(nonce))
print(type(nonce))
bitlist = []
for x in (0, 20):
    bitlist.append(str(0))
nonce_number = ''.join(bitlist)
nonce_number = 23 * b'\x00'
nonce_number = nonce_number + b'\x01'
nonce_prefix = 3
hex_string = '0x{:02x}'.format(nonce_prefix)
# print(bytes.fromhex(hex_string))
print(nonce_number)

#print(add_binary_nums('000000000000000000001001', '1'))
#rs = add_binary_nums(23*8*'0'+'11111110', '1')
rs = add_binary_nums(23*8*'0'+4*'0'+bin(10)[2:], '1')

print(rs)
print(type(rs))
print(len(rs))
print(bitstring_to_bytes(rs))
print(type(bitstring_to_bytes(rs)))
print(len(bitstring_to_bytes(rs)))

key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
box = nacl.secret.SecretBox(key)


# This is our message to send, it must be a bytestring as SecretBox will
#   treat it as just a binary blob of data.
message = b"The president will be exiting through the lower levels"
print(type(message))


nonce_prefix = 4
nonce_number = 5

nonce_prefix_value = (nonce_prefix-len(bin(nonce_number)[2:])) * '0' + bin(nonce_number)[2:]
print("here")
print(nonce_prefix_value)

nonce_sequence = ((24*8) - nonce_prefix ) * '0'
print(nonce_sequence)
incremented_seq = add_binary_nums(nonce_sequence, '1')
incremented_seq = add_binary_nums(incremented_seq, '1')
print(incremented_seq)
final_nonce = bitstring_to_bytes(incremented_seq + nonce_prefix_value)
print(final_nonce)
encrypted = box.encrypt(message, final_nonce)
#encrypted = box.encrypt(message, bitstring_to_bytes(rs))
print (box.decrypt(encrypted))
test = '00000000'

print(len(bin(1)[2:]))
print(bin(1)[2:])