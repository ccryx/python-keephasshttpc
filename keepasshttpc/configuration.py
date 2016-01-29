import base64

from os.path import expanduser


# TODO: make this a fully fledged configuration management


def get_crypto_key():
    identifier = None
    key = None
    # TODO: define this path somewhere else
    path = expanduser('~') + '/.kphttpc/key'
    try:
        with open(path) as keyfile:
            lines = keyfile.readlines()
            identifier = lines[0][:-1]
            key = base64.b64decode(lines[1][:-1].encode('utf-8'))
    except FileNotFoundError:
        # TODO: handle more io errors
        return None
    return [identifier, key]


def set_crypto_key(identifier, key):
    path = expanduser('~') + '/.kphttpc/key'
    with open(path, 'w') as keyfile:
        keyfile.write(identifier+'\n')
        keyfile.write(base64.b64encode(key).decode('utf-8')+'\n')
