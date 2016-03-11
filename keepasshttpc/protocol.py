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

import sys
import json
import urllib.request
import base64

import keepasshttpc.cryptohelpers as ch
import keepasshttpc.configuration as cfg


def send(request, plugin_url='http://localhost:19455'):
    headers = {}
    headers['Content-Type'] = 'application/json'
    request_bytes = json.dumps(request).encode('utf-8')
    req = urllib.request.Request(plugin_url, request_bytes, headers)
    response = None
    try:
        with urllib.request.urlopen(req) as res:
            response_bytes = res.read()
            response = json.loads(response_bytes.decode('utf-8'))
    except urllib.error.HTTPError as e:
        print('code: ' + str(e.code) + '\n' +
              'reason:'+e.reason+'\n' +
              str(e.headers), file=sys.stderr)
    except urllib.error.URLError as e:
        print('error: '+str(e.reason), file=sys.stderr)
    return response


def set_verifier(request, inkey=None):
    identifier = None
    key = None
    if inkey is None:
        # happens when we don't want to associate
        info = cfg.get_crypto_key()
        if info is None:
            # TODO: proper execption handling
            return None
        [identifier, key] = info
        request['Id'] = identifier
    else:
        key = inkey

    iv = ch.generate_IV()
    iv64str = base64.b64encode(iv).decode('utf-8')
    request['Nonce'] = iv64str
    request['Verifier'] = base64.b64encode(
        ch.encrypt(iv64str, key, iv)).decode('utf-8')
    return [identifier, key]


def verify_response(response, key, identifier=None):
    if not response['Success']:
        return False

    iv = base64.b64decode(response['Nonce'].encode('utf-8'))
    crypted = base64.b64decode(response['Verifier'])
    value = ch.decrypt(crypted, key, iv)
    valid = value == response['Nonce']
    if identifier is not None:
        valid = valid and identifier == response['Id']
    return valid


def decrypt_entry(entry, key, iv):
    for k, v in entry.items():
        if k is not 'StringFields':
            entry[k] = ch.decrypt(base64.b64decode(v), key, iv)

    if 'StringFields' in entry:
        fields = []
        for field in entry['StringFields']:
            field['Key'] = ch.decrypt(field['Key'], key, iv, True)
            field['Value'] = ch.decrypt(field['Value'], key, iv, True)
            fields = fields + [field]
        entry['StringFields'] = fields


def associate():
    """Associate with KeepassHTTP

    """
    key = ch.generate_key()
    request = {'RequestType': 'associate',
               'Key': base64.standard_b64encode(key).decode('utf-8')}
    set_verifier(request, key)
    response = send(request)
    if response is not None:
        if verify_response(response, key):
            identifier = response['Id']
            cfg.set_crypto_key(identifier, key)


def test_associate(triggerUnlock=False):
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


def retrieve_credentials(url, submiturl=None, triggerUnlock=False):
    if not test_associate(triggerUnlock):
        return None

    request = {'RequestType': 'get-logins',
               'SortSelection': True,
               'TriggerUnlock': triggerUnlock}
    info = set_verifier(request)
    if info is None:
        return None
    [identifier, key] = info
    iv64 = request['Nonce']
    iv = base64.b64decode(iv64.encode('utf-8'))

    request['Url'] = base64.b64encode(ch.encrypt(url, key, iv)).decode('utf-8')

    if submiturl is not None:
        request['SubmitUrl'] = base64.b64encode(
            ch.encrypt(submiturl, key, iv)).decode('utf-8')

    response = send(request)

    entries = []

    if response is not None:
        # set_current_KeePassHttp_version(response['Version'])
        if verify_response(response, key, identifier):
            iv64_r = response['Nonce']
            iv_r = base64.b64decode(iv64_r.encode('utf-8'))

            for e in response['Entries']:
                decrypt_entry(e, key, iv_r)

            entries = response['Entries']

    return entries


def get_all_logins(triggerUnlock=False):
    if not test_associate(triggerUnlock):
        return None

    request = {'RequestType': 'get-all-logins',
               'SortSelection': True,
               'TriggerUnlock': triggerUnlock}
    info = set_verifier(request)
    if info is None:
        return None
    [identifier, key] = info
    # iv64 = request['Nonce']
    # iv = base64.b64decode(iv64.encode('utf-8'))

    response = send(request)

    entries = []

    if response is not None:
        # set_current_KeePassHttp_version(response['Version'])
        if verify_response(response, key, identifier):
            iv64_r = response['Nonce']
            iv_r = base64.b64decode(iv64_r.encode('utf-8'))

            for e in response['Entries']:
                decrypt_entry(e, key, iv_r)

            entries = response['Entries']

    return entries
