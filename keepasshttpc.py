import json, urllib.request, base64, sys

from os.path import expanduser

from Crypto.Cipher import AES
from Crypto import Random

associated = False
isDatabaseClosed = False
isKeepassHttpAvailable = False
isEncryptionKeyUnrecognized = False
currentKeePassHttp = {'version':0, 'versionParsed':0}

keySize = 32;
pluginUrl= 'http://localhost:19455'
latestVersionUrl = 'https://passifox.appspot.com/kph/latest-version.txt'
cacheTimeout = 30 * 1000 # milliseconds

##########################################
# Helper functions
##########################################
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


def decryptEntry(entry, key, iv):
    for k,v in entry.items():
        if k is not 'StringFields':
            entry[k] = decrypt(base64.b64decode(v), key, iv)

    if 'StringFields' in entry:
        fields = []
        for field in entry['StringFields']:
            field['Key'] = decrypt(field['Key'], key, iv, True)
            field['Value'] = decrypt(field['Value'], key, iv, True)
            fields = fields + [field]
        entry['StringFields'] = fields


def set_current_KeePassHttp_version(version):
    if version is not None:
        currentKeePassHttp['version'] = version
        currentKeePassHttp['versionParsed'] = int(version.replace('.',''))


def retrieve_credentials(url, submiturl=None, triggerUnlock=False):
    if not test_associate(triggerUnlock):
        return None

    request = {'RequestType': 'get-logins', 'SortSelection': True, 'TriggerUnlock': triggerUnlock}
    info = set_verifier(request)
    if info is None:
        return None
    [identifier, key] = info
    iv64 = request['Nonce']
    iv = base64.b64decode(iv64.encode('utf-8'))

    request['Url'] = base64.b64encode(encrypt(url, key, iv)).decode('utf-8')

    if submiturl is not None:
        request['SubmitUrl'] = base64.b63encode(encrypt(submiturl, key, iv)).decode('utf-8')

    response = send(request)

    entries = []

    if response is not None:
        set_current_KeePassHttp_version(response['Version'])
        if verify_response(response, key, identifier):
            iv64_r = response['Nonce']
            iv_r = base64.b64decode(iv64_r.encode('utf-8'))

            for e in response['Entries']:
                decryptEntry(e, key, iv_r)

            entries = response['Entries']

    return entries


def get_all_logins(triggerUnlock=False):
    if not test_associate(triggerUnlock):
        return None

    request = {'RequestType': 'get-all-logins', 'SortSelection': True, 'TriggerUnlock': triggerUnlock}
    info = set_verifier(request)
    if info is None:
        return None
    [identifier, key] = info
    iv64 = request['Nonce']
    iv = base64.b64decode(iv64.encode('utf-8'))

    response = send(request)

    entries = []

    if response is not None:
        set_current_KeePassHttp_version(response['Version'])
        if verify_response(response, key, identifier):
            iv64_r = response['Nonce']
            iv_r = base64.b64decode(iv64_r.encode('utf-8'))

            for e in response['Entries']:
                decryptEntry(e, key, iv_r)

            entries = response['Entries']

    return entries


def test_associate(triggerUnlock = False):
    request = {'RequestType': 'test-associate', 'TriggerUnlock': triggerUnlock}
    info = set_verifier(request)
    if info is None:
        return False

    [identifier, key] = info

    response = send(request)
    if response is not None:
        if verify_response(response, key, identifier):
            return True
        else:
            return False


def associate():
    """Associate with KeepassHTTP

    """
    key = Random.get_random_bytes(32)
    #request = {'RequestType': 'associate'}
    request = {'RequestType': 'associate', 'Key': base64.standard_b64encode(key).decode('utf-8')}
    info = set_verifier(request, key)
    response = send(request)
    if response is not None:
        if verify_response(response, key):
            identifier = response['Id']
            set_crypto_key(identifier, key)
            associated = True
        else:
            associated = False


def set_verifier(request, inkey=None):
    identifier = None
    key = None
    if inkey is None:
        # happens when we don't want to associate
        info = get_crypto_key()
        if info is None:
            #TODO: proper execption handling
            return None
        [identifier, key] = info
        request['Id'] = identifier
    else:
        key = inkey

    iv = Random.new().read(AES.block_size)
    iv64str = base64.b64encode(iv).decode('utf-8')
    request['Nonce'] = iv64str
    request['Verifier'] = base64.b64encode(encrypt(iv64str, key, iv)).decode('utf-8')
    return [identifier, key]


def verify_response(response, key, identifier=None):
    if not response['Success']:
        return False

    iv = base64.b64decode(response['Nonce'].encode('utf-8'))
    crypted = base64.b64decode(response['Verifier'])
    value = decrypt(crypted, key, iv)
    valid = value == response['Nonce']
    if identifier is not None:
        valid = valid and identifier == response['Id']
    return valid


def get_crypto_key():
    identifier = None
    key = None
    #TODO: define this path somewhere else
    path = expanduser('~') + '/.kphttpc/key'
    try:
        with open(path) as keyfile:
            lines = keyfile.readlines()
            identifier = lines[0][:-1]
            key = base64.b64decode(lines[1][:-1].encode('utf-8'))
    except FileNotFoundError:
        #TODO: handle more io errors
        return None
    return [identifier, key]


def set_crypto_key(identifier, key):
    path = expanduser('~') + '/.kphttpc/key'
    with open(path, 'w') as keyfile:
        keyfile.write(identifier+'\n')
        keyfile.write(base64.b64encode(key).decode('utf-8')+'\n')


def send(request):
    headers = {}
    headers['Content-Type'] = 'application/json'
    request_bytes = json.dumps(request).encode('utf-8')
    req = urllib.request.Request(pluginUrl, request_bytes, headers)
    response = None
    try:
        with urllib.request.urlopen(req) as res:
            response_bytes = res.read()
            response = json.loads(response_bytes.decode('utf-8'))
    except urllib.error.HTTPError as e:
        print('code: '+str(e.code)+'\nreason:'+e.reason+'\n'+str(e.headers), file=sys.stderr)
    except urllib.error.URLError as e:
        print('error: '+str(e.reason), file=sys.stderr)
    return response
