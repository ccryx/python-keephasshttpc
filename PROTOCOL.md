# How to communicated with the KeepassHttp server

Communication happens over http (default port 19455) POSTs (?) using json in the message body.
The request type is specified by the RequestType key.
The following table lists the possible values for RequestType, required and optional additional keys and comments.
The values of all fields are utf-8 strings.

|RequestType      |Required Keys           |Optional Keys|Description|
|-----------------|------------------------|-------------|-----------|
|associate        |Nonce, Verifier, Key    |             |Associate with the KeepassHttp server. This is necessary for all the other requests (except test-associate).|
|generate-password|Id, Nonce, Verifier     |             |Genere a password (using the most recently used password generator settings?).                              |
|get-all-logins   |Id, Nonce, Verifier     |             |Get all logins from the KeePass database.                                                                   |
|get-logins       |Id, Nonce, Verifier, Url|SubmitUrl    |Get the logins for the specified Url.                                                                       |
|get-logins-count |Id, Nonce, Verifier     |             |Get the number of logins (for the speified Url?).                                                           |
|set-login        |Id, Nonce, Verifier, Url|             |No idea yet.                                                                                                |
|test-associate   |Id, Nonce, Verifier     |             |Test if the current client is associated with the currently opened KeePass database.                        |

The requests are described in more detail in the following paragraphs.
The Nonce and Verifier keys used in every request are necessary for encrypting/decrypting encrypted fields.
KeePassHttp uses the AES CBC mode which requires an initialization vector (IV) for encryption and decryption.
The 16 byte long IV is randomly generated for each request encoded with base64 and sent as the value for the `Nonce` key.
In order to make sure everything's ok (?) the KeePassHttp protocol uses a `Verifier`.
To generate the `Verifier`, the `Nonce` is padded, encrypted and base64 encoded.
At first it might seems weird that the `Nonce` needs to be padded, because the IV has the correct minimum length.
The base64 encoded utf-8 string is not, however, so padding is necessary.

## test-associate
Required keys: Id, Nonce, Verifier
This request should be sent prior to trying to interact further with the KeePassHttp server.
The Id is the saved client Id.
If there is no saved client Id, the client should instead send an associate request.

## associate
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
TODO: explain `Hash` key
