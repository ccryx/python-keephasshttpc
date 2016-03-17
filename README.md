# python-keephasshttpc
A keepasshttp client library written in python.

**WARNING:** I am not a cryptographer. I may have messed up the AES encryption/decryption process somewhere in a way that compromises the security of your KeePass database. You also need to remember that your AES key used for decrypting the communication to the keepasshttp server is stored in plain text on your hard drive (but this is not much different to using Firefox or Chrome without a master password).

This python library can be used to communicate with a server that implements the keepasshttp protocol.
Currently you can use it to associate with a database and retrieve logins for a specified url.

I hope to have a complete implementation eventually but for now I will mostly fix up the current on since I don't have much time.
Contributions are of course always welcome.

The code is very similar to the javascript implementation in the Chrome plugin [ChromeIPass](https://github.com/pfn/passifox) since I used it as a reference.

## Dependencies
python-keepasshttpc requires **python 3** and **pycrypto**. I am personally using it with python 3.5 and pycrypto 2.6.1.

## Installation
Until python-keepasshttpc becomes an installable package you can use the following isntructions to install it.

1. `git clone https://github.com/ccryx/python-keephasshttpc.git`
2. `cd python-keepasshttpc`
3. `mkdir -p ~/.local/lib/python3.5/site-packages`
4. `cp -r keepasshttpc ~/.local/lib/python3.5/site-packages/`<sup>1</sup>
5. `cp keepasshttpc.py ~/bin` (optional)<sup>2</sup>

Note 1: This is your user's `site-packages` path. See [Installing Python Modules (Legacy version)]{https://docs.python.org/3.5/install/} and [PEP 0370]{https://www.python.org/dev/peps/pep-0370/} for more information.
Note 2: This assumes that `~/bin` is on your PATH. You can place the `keepasshttpc.py` script anywhere on you PATH. You only need to do this if you want to you the script to interact with a keepasshttp server.

python-keepasshttpc - communicate with a keepasshttp server
Copyright (C) 2015-2016  Florian Merkel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
