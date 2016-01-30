#!/usr/bin/env python3

import argparse

from keepasshttpc.protocol import (test_associate, associate,
                                   retrieve_credentials, get_all_logins)


def do_get_logins(args):
    output = []
    creds = retrieve_credentials(args.url, triggerUnlock=args.unlock)
    for c in creds:
        o = {}
        if args.info is None:
            o['name'] = c['Name']
            o['login'] = c['Login']
            o['password'] = c['Password']
        else:
            if 'name' in args.info:
                o['name'] = c['Name']
            if 'login' in args.info:
                o['login'] = c['Login']
            if 'password' in args.info:
                o['password'] = c['Password']
            if 'uuid' in args.info:
                o['uuid'] = c['Uuid']
        output.append(o)
    if len(output) == 1:
        print(output[0])
    else:
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
                                   choices=['name', 'user', 'password', 'uuid'],
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
