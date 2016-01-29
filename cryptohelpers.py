from Crypto.Cipher import AES
from Crypto import Random


key_size = 32


def aes_pad(plaintext):
    pad_len = 16-len(plaintext) % 16
    pad_chr = chr(pad_len)
    return plaintext + (pad_chr * pad_len)


def aes_unpad(plaintext):
    pad_len = ord(plaintext[-1])
    if pad_len <= 16:
        return plaintext[:-pad_len]
    else:
        return plaintext


def encrypt(plaintext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(aes_pad(plaintext))


def decrypt(crypttext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return aes_unpad(cipher.decrypt(crypttext).decode('utf-8'))


def generate_key():
    return Random.get_random_bytes(key_size)


def generate_IV():
    return Random.new().read(AES.block_size)
