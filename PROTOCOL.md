# How to communicated with the KeepassHttp server

Communication happens over http (default port 19455) POSTs (?) using json in the message body.
The request type is specified by the RequestType key.
The following table lists the possible values for RequestType, required and optional additional keys and comments.
The values of all fields are utf-8 strings.

|RequestType      |Required Keys           |Optional Keys|Description|
|-----------------|------------------------|-------------|-----------|
|test-associate   |Id, Nonce, Verifier     |             |Test if the current client is associated with the currently opened KeePass database.                        |
|associate        |Nonce, Verifier, Key    |             |Associate with the KeepassHttp server. This is necessary for all the other requests (except test-associate).|
|get-logins       |Id, Nonce, Verifier, Url|SubmitUrl    |Get the logins for the specified Url.                                                                       |
|get-all-logins   |Id, Nonce, Verifier     |             |Get all logins from the KeePass database.                                                                   |
|get-logins-count |Id, Nonce, Verifier, Url|             |Get the number of logins (for the speified Url?).                                                           |
|generate-password|Id, Nonce, Verifier     |             |Genere a password (using the most recently used password generator settings?).                              |
|set-login        |Id, Nonce, Verifier, Url|             |No idea yet.                                                                                                |

The requests are described in more detail in the following paragraphs.
The Nonce and Verifier keys used in every request are necessary for encrypting/decrypting encrypted fields.
KeePassHttp uses the AES CBC mode which requires an initialization vector (IV) for encryption and decryption.
The 16 byte long IV is randomly generated for each request encoded with base64 and sent as the value for the `Nonce` key.
In order to make sure everything's ok (?) the KeePassHttp protocol uses a `Verifier`.
To generate the `Verifier`, the `Nonce` is padded, encrypted and base64 encoded.
At first it might seems weird that the `Nonce` needs to be padded, because the IV has the correct minimum length.
The base64 encoded utf-8 string is not, however, so padding is necessary.
TODO: explain `Success`, `Version`, `Hash`, `TriggerUnlock` keys.

### test-associate
Required keys: Id, Nonce, Verifier  
This request should be sent prior to trying to interact further with the KeePassHttp server.
The Id is the saved client Id.
If there is no saved client Id, the client should instead send an associate request.
An example request could look like this:
```
{'Id': 'testblasdlkj',  'Nonce': 'c8Wko/EGoPPd+DIcM4MlXg==', 'Verifier': 'SwI3JmaLU15+8NVJjus0HQ1aiFepN5wuaRgcSu2N+5w=', 'TriggerUnlock': False,}
```
If the client is associated with the server, the response will contain key/value pair `Success: True`.
A sample response coul look like this:
```
{'RequestType': 'test-associate', 'Nonce': 'LQPfGUcPHFhLz7hVmDDhwA==', 'Success': True, 'Verifier': 'XB/KWYXIKFTArCh40fujmWZr5vEEZhf6Y498Zw+Xob0=', 'Id': 'testblasdlkj', 'Count': 0, 'Version': '1.8.4.0', 'Hash': '285b3e8041c505324132407b3a8bee35831e6dd9'}
```
For an unassociated client response could look like this:
```
{'Success': False, 'RequestType': 'test-associate', 'Count': 0, 'Version': '1.8.4.0', 'Hash': '285b3e8041c505324132407b3a8bee35831e6dd9'}
```

### associate
Required keys: Nonce, Verifier, Key  
This request is used to associate with the KeePassHttp server for the current KeePass database.
It needs to be sent if the client is not associated  with the KeePass Http server.
The `Key` key contains the base64 encoded 256 bit AES encryption key.
It is randomly generated.
An example request could look like this:
```
{'RequestType': 'associate', 'Key': 'OP/rKyOifj60Xc5UTORll92KtJ03uWowqE7vTMHAUpA=', 'Nonce': 'KTBmnSTGTEvri1embt/AKA==', 'Verifier': 'rSOwzupE5dv4zgwkIX6GXnl9dGRJ1c74J83LatL+Hkk='} 
```
When the server receives an associate request a dialog is presented for the user to provide an identifier for the key.
If the user does so and confirms the identifier, the server responds with a response similar to this one:
```
{'RequestType': 'associate', 'Nonce': 'XWlCr74qgqRBNgIjjkF1FA==', 'Hash': '285b3e8041c505324132407b3a8bee35831e6dd9', 'Id': 'testblasdlkj', 'Verifier': 'V92A/xByvoMOizvOq1HHrJ+0WpikZoNgEGsDlOnsMts=', 'Version': '1.8.4.0', 'Success': True, 'Count': 0}
```
The `Id` must be saved and used for further requests that assume that the client is associated with the server.
If the user doesn't confirm, the response will look like this:
```
{'RequestType': 'associate', 'Version': '1.8.4.0', 'Hash': '285b3e8041c505324132407b3a8bee35831e6dd9', 'Success': False, 'Count': 0}
```

### get-logins
Required keys: Id, Nonce, Verifier, Url  
Optional keys: SortSelection, SubmitUrl  
This request is used for getting logins identified by the speicifed `Url` key.  
TODO: remark about regex.  
Its value is the encrypted and base64 encoded url string.  
TODO: explain `SubmitUrl`.  
An example request could look like this:
```
{'RequestType': 'get-logins', 'Url': '<base64 encoded url>', 'SortSelection': True, 'TriggerUnlock': False, 'Id': 'kphttpc', 'Verifier': 'nr9g2liy5QHXMTFw5qnA0s23PKkzCupwQqsRhAPTKDY=', 'Nonce': '0I5ikdcjk9gsQNo1c8nXTQ=='}
```
The server response will contain an array accessible with the key `Entries` that has all the entries that match the given `Url`.
If the optional key `SortSelection` is set to `True`, the `Entries` array will be sorted by the quality of the match from best to worst.
An individual entry has the following keys:
* Name - The entry's name in the KeePass database
* Login - The entry's login
* Password - The entry's password
* Uuid - A universially unique identifier
The entries' values are all encrypted and base64 encoded.
The Response will also have its `Count` key set to the number of logins found.
It could look like this:
```
{'RequestType': 'get-logins', 'Nonce': 'OndT6Aes2Zpbe3bXaUG+kA==', 'Entries': [{'Password': '<base64 encoded password>', 'Login': '<base64 encoded user name>', 'Uuid': 'HZx3ZJXO+sHStbpqdJEkdltTNmeLyC0WKPORaqHTcCREbX8aBno6aGBo0HC86XX5', 'Name': '<base64 encoded uuid>'}], 'Success': True, 'Verifier': '0l22d9QeDuc5lAzg31220q/H/B62sdQncjZDTU85McE=', 'Id': 'kphttpc', 'Count': 1, 'Version': '1.8.4.0', 'Hash': '285b3e8041c505324132407b3a8bee35831e6dd9'}
```
If no logins are found, the `Entries` array will be empty.

### get-all-logins
Required keys: Id, Nonce, Verifier  
This request is used for getting all logins that have a domain or url in the Url field (and possible in the entry name).
The response has an `Entries` key that contains an array similar to the one returned by the `get-logins` request with the difference that the entries contain no passwords.
The `Count` value is always 0, no matter how many entries were returned.

### generate-password
### set-login
