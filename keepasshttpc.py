#!/usr/bin/env python3

#   keepasshttpc - communicate with a keepasshttp server
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

import argparse

from keepasshttpc.protocol import (test_associate, associate,
                                   retrieve_credentials, get_all_logins)


def add_default_info(creds, out):
    out['name'] = creds['Name']
    out['login'] = creds['Login']
    out['password'] = creds['Password']


def print_relevant_info(info, creds):
    print(creds[info[0].upper()+info[1:]])


def add_relevant_info(info, creds, out):
    if 'name' in info:
        out['name'] = creds['Name']
    if 'login' in info:
        out['login'] = creds['Login']
    if 'password' in info:
        out['password'] = creds['Password']
    if 'uuid' in info:
        out['uuid'] = creds['Uuid']


def do_get_logins(args):
    output = []
    creds = retrieve_credentials(args.url, triggerUnlock=args.unlock)
    for c in creds:
        o = {}
        if args.info is None:
            add_default_info(c, o)
            output.append(o)
        elif len(args.info) == 1:
            print_relevant_info(args.info[0], c)
            # return
        else:
            add_relevant_info(args.info, c, o)
            output.append(o)

    if len(output) == 1:
        print(output[0])
    elif len(output) > 1:
        print(output)


def not_implemented(args):
    print('Not implemented')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Communicate with a ' +
                                     'KeePassHTTP server.')
    subparsers = parser.add_subparsers()

    parser_test_associate = subparsers.add_parser('test-associate')
    parser_test_associate.set_defaults(func=(
        lambda args: print(test_associate(args.unlock)))
    )

    parser_associate = subparsers.add_parser('associate')
    parser_associate.set_defaults(func=(
        lambda args: print(associate(args.unlock)))
    )

    parser_get_logins = subparsers.add_parser('get-logins')
    parser_get_logins.add_argument('--info',
                                   choices=['login',
                                            'name',
                                            'password',
                                            'uuid'],
                                   action='append')
    parser_get_logins.add_argument('url')
    parser_get_logins.set_defaults(func=do_get_logins)

    parser_get_all_logins = subparsers.add_parser('get-all-logins')
    parser_get_all_logins.set_defaults(func=(
        lambda args: print(get_all_logins(args.unlock)))
    )

    parser_get_logins_count = subparsers.add_parser('get-logins-count')
    parser_get_logins_count.add_argument('url')
    parser_get_logins_count.set_defaults(func=not_implemented)

    parser_generate_password = subparsers.add_parser('generate-password')
    parser_generate_password.set_defaults(func=not_implemented)

    parser_set_login = subparsers.add_parser('set-login')
    parser_set_login.set_defaults(func=not_implemented)

    parser.add_argument('--unlock', action='store_true')

    args = parser.parse_args()
    args.func(args)
