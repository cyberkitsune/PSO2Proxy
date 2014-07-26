# PSO2Proxy
PSO2Proxy is a open source protocol proxy for the Japanese MMORPG, Phantasy Star Online 2 written in python. It allows the game's packet data to be unencrypted, logged, parsed and modified to both the client and server. It can also be used to connect to the game's servers if a client is blocked from normally connecting for any reason.

## Note
This program allows you to host your own PSO2Proxy on a server you have access to. **If you just want to play the game via the proxy, a public PSO2Proxy server is provided for both users who can't connect to PSO2 and users who want to contribute data for packet analysis at [pso2proxy.cyberkitsune.net](http://pso2proxy.cyberkitsune.net/). Below are the instructions for installing and setting up your own PSO2Proxy server.**

Feel free to contact us on [IRC](irc://irc.badnik.net/pso2proxypublic): irc.badnik.net, #pso2proxypublic
## Installing
PSO2Proxy uses the [Twisted Framework](https://twistedmatrix.com/trac/) and [PyCrypto](https://www.dlitz.net/software/pycrypto/). Please install these from their respective websites.

If you have a git commandline client, setuptools and pip installed, you can install it like this:

```
    git clone https://github.com/cyberkitsune/PSO2Proxy.git
    cd PSO2Proxy
    pip install -r requirements.txt
```

## Configuring the Server
To configure the server, run it once to generate the pso2proxy.config.json, then edit that. You need at least your Public IP address set and your adapter IP set if it's different from your public ip. If unsure, leave the bindIp `0.0.0.0`.
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
### Rebind hosts file
To get clients to connect to your proxy, they need to think SEGA's servers are your servers. An easy way to do this is to modify Windows's hosts file, add the following code below to the hosts file in `c:\Windows\System32\Drivers\etc\hosts`, replacing 0.0.0.0 with the proxy's **IP address**.
```
0.0.0.0 gs001.pso2gs.net #Also ship 1
0.0.0.0 gs016.pso2gs.net #Also ship 2
0.0.0.0 gs031.pso2gs.net #Also ship 3
0.0.0.0 gs046.pso2gs.net #Also ship 4
0.0.0.0 gs061.pso2gs.net #Also ship 5
0.0.0.0 gs076.pso2gs.net #Also ship 6
0.0.0.0 gs091.pso2gs.net #Also ship 7
0.0.0.0 gs106.pso2gs.net #Also ship 8
0.0.0.0 gs121.pso2gs.net #Also ship 9
0.0.0.0 gs136.pso2gs.net #Also ship 10
```
### Use your RSA keys
To get the proxy to decrypt the client's packets, place the publickey.blob you generated in the same folder as PSO2.exe, and rename the RSAKeyInjector.dll to ddraw.dll in that same folder. **If you use PSO2Tweaker to launch PSO2**, enable the item translation patch and rename ddraw.dll to rsainject.dll instead.

