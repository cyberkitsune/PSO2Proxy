# PSO2Proxy
PSO2Proxy is a open soruce protocol proxy for the Japanese MMORPG, Phantasy Star Online 2 written in python. It allows the game's packet data to be unencrypted, logged, parsed and modified to both the client and server. It can also be used to connect to the game's servers if a client is blocked from normally connecting for any reason.

A public PSO2Proxy server is provided for both users who can't connect to PSO2 and users who want to contribute data for packet analysis at [pso2proxy.cyberkitsune.net](http://pso2proxy.cyberkitsune.net/). Below are the instructions for installing and setting up your own PSO2Proxy server.
## Installing
PSO2Proxy uses the [Twisted Framework](https://twistedmatrix.com/trac/) and [PyCrypto](https://www.dlitz.net/software/pycrypto/). Please install these from their respective websites.

If you have setuptools and pip installed, use this command:

`pip install twisted pycrypto`
## Configuring the Server
In order to make the server work, you need to (at the very least) specify your system's public IP address in config.py and install a RSA private key of your own, and a SEGA RSA Public key imported from the PSO2 Client.
## RSA Keys
### Your private / public keypair
You'll need to generate a RSA public and private keypair for your server and your proxy's clients for the proxy to work. You can use OpenSSL to do this.

Generate the private key:

`openssl genpkey -out myKey.pem -algorithm rsa -pkeyopt rsa_keygen_bits:1024`

Generate a compatible publickey.blob for your clients:

`openssl rsa -in myKey.pem -outform MS\ PUBLICKEYBLOB -pubout -out publickey.blob`
### SEGA's Public key
You'll ALSO need to import SEGA's RSA public keys from the PSO2 client. For instructions on how to get SEGAKey.blob, see [this wiki page](https://github.com/cyberkitsune/PSO2Proxy/wiki/Getting-SEGA's-RSA-Keys).

To convert SEGAKey.blob to SEGAKey.pem, use this OpenSSL command:

`openssl rsa -pubin -inform MS\ PUBLICKEYBLOB -in SEGAKey.blob -outform PEM -out SEGAKey.pem`

## Getting clients to connect
`TODO`
