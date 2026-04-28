import base64
import struct
from binascii import unhexlify
from impacket.krb5.crypto import _AES256CTS


b64 = input("Enter the base64 string: ")

blob = base64.b64decode(b64)
raw = (blob.hex())

blob_raw = unhexlify(raw)

# gMSA blob: current password starts at offset 0, length 256 bytes (UTF-16LE)
pwd = blob_raw[:256].decode('utf-16-le', 'replace').encode('utf-8')
raw_salt = input("Enter the salt value: ")
salt = raw_salt.encode()  # FIX: use input properly

aes256 = _AES256CTS.string_to_key(pwd, salt, b'\x00\x00\x10\x00').contents.hex()
print(f"AES256 Key: {aes256}")