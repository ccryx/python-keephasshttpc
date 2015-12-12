# python-keephasshttpc
A keepasshttp client library written in python.

**WARNING:** I am not a cryptographer. I may have messed up the AES encryption/decryption process somewhere in a way that compromises the security of your KeePass database. You also need to remember that your AES key used for decrypting the communication to the keepasshttp server is stored in plain text on your hard drive (but this is not much different to using Firefox or Chrome without a master password).

This python library can be used to communicate with a server that implements the keepasshttp protocol.
Currently you can use it to associate with a database and retrieve logins for a specified url.

I hope to have a complete implementation eventually but for now I will mostly fix up the current on since I don't have much time.
Contributions are of course always welcome.

The code is very similar to the javascript implementation in the Chrome plugin [ChromeIPass](https://github.com/pfn/passifox) since I used it as a reference.


python-keepasshttpc  Copyright (C) 2015  Florian Merkel.  
This program comes with ABSOLUTELY NO WARRANTY.  
This is free software, and you are welcome to redistribute it under certain conditions. 
See LICENSE.md for details.
