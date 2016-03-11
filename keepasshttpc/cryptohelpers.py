#   python-keepasshttpc - communicate with a keepasshttp server
#   Copyright (C) 2015-2016  Florian Merkel
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, version 3 of the License.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
