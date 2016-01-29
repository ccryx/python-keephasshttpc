import argparse

from protocol import (test_associate, associate, retrieve_credentials,
                      get_all_logins)

currentKeePassHttp = {'version': 0, 'versionParsed': 0}

pluginUrl = 'http://localhost:19455'
latestVersionUrl = 'https://passifox.appspot.com/kph/latest-version.txt'


##########################################
# Helper functions
##########################################


def set_current_KeePassHttp_version(version):
    if version is not None:
        currentKeePassHttp['version'] = version
        currentKeePassHttp['versionParsed'] = int(version.replace('.', ''))


def main(args):
    if 'info' == args.command:
        print('executing command ' + args.command)

    elif 'test-associate' == args.command:
        print(test_associate(args.unlock))

    elif 'associate' == args.command:
        print(associate())

    elif 'get-logins' == args.command:
        if args.url is not None:
            for u in args.url:
                print(retrieve_credentials(u,
                                           args.submiturl,
                                           args.unlock))
        else:
            print('No Url was given')

    elif 'get-all-logins' == args.command:
        print(get_all_logins(args.unlock))

    elif 'get-logins-count' == args.command:
        print(args.command + ': not implemented')

    elif 'generate-password' == args.command:
        print(args.command + ': not implemented')

    elif 'set-login' == args.command:
        print(args.command + ': not implemented')

    elif 'info' == args.command:
        print(args.command + ': not implemented')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Communicate with a ' +
                                     'KeePassHTTP server.')

    parser.add_argument('--command', default='info',
                        choices=['test-associate',
                                 'associate',
                                 'get-logins',
                                 'get-all-logins',
                                 'get-logins-count',
                                 'generate-password',
                                 'set-login',
                                 'info'],
                        required=True)
    parser.add_argument('--url', action='append')
    parser.add_argument('--submiturl', action='append')
    parser.add_argument('--unlock', action='store_true')
    # * test-associate(): True or False, possibly some more info
    # * get-logins(Url [,SubmitUrl]): JSON Array with logins matching Url
    # * get-all-logins(): JSON Array with all logins (no passwords)
    # * get-logins-count: Integer with the number of logins matching Url
    # * generate-password: the generated password
    # * set-login: No idea
    args = parser.parse_args()
    main(args)
