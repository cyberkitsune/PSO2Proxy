# PSO2Proxy
PSO2Proxy is a open source protocol proxy for the Japanese MMORPG, Phantasy Star Online 2 written in python. It allows the game's packet data to be unencrypted, logged, parsed and modified to both the client and server. It can also be used to connect to the game's servers if a client is blocked from normally connecting for any reason.

## Note
This program allows you to host your own PSO2Proxy on a server you have access to. 
**If you just want to play the game via the proxy, a public PSO2Proxy server is available for users who can't connect to PSO2 and users who want to contribute data for packet analysis. This server can be found at [pso2proxy.cyberkitsune.net](http://pso2proxy.cyberkitsune.net/). Below are the instructions for installing and setting up your own PSO2Proxy server.**

If you require assistance, feel free to contact us on [IRC](irc://irc.badnik.net/pso2proxypublic): irc.badnik.net, #pso2proxypublic
## Installing
PSO2Proxy uses the [Twisted Framework](https://twistedmatrix.com/trac/) and [PyCrypto](https://www.dlitz.net/software/pycrypto/). Please install these from their respective websites or use the commands below depending on your distrubution.

####If you have a Debian based system, you can install via apt-get for the depends:

```
    sudo apt-get install python-twisted python-crypto python-yaml python-faulthandler openssl git
    git clone https://github.com/cyberkitsune/PSO2Proxy.git ~/PSO2Proxy
```

####If your server is running Debian Wheezy, you need to get a more up to date version of the python-twisted package from backports:
```
    echo deb http://http.debian.net/debian wheezy-backports main|sudo tee /etc/apt/sources.list.d/wheezy-backports.list>/dev/null
    sudo apt-get update
    sudo apt-get -t wheezy-backports install python-twisted
```

####For RPM based systems, like Amazon Linux AMI on Amazon EC2 (Amazon Web Services Instance):

```
    sudo yum install python-pip gcc python-devel git
    git clone https://github.com/cyberkitsune/PSO2Proxy.git ~/PSO2Proxy
    cd ~/PSO2Proxy
    sudo pip install -r requirements.txt
```

####Others: If you have a git commandline client, setuptools and pip installed, you can install it like this:

```
    git clone https://github.com/cyberkitsune/PSO2Proxy.git ~/PSO2Proxy
    cd ~/PSO2Proxy
    pip install -r requirements.txt
```

## Start up the Sever for the first time
```
    cd ~/PSO2Proxy/proxy
    python ./PSO2Proxy.py
```

## Configuring the Server
To configure the server, run it once to generate the pso2proxy.config.yml in `~/PSO2Proxy/proxy/cfg/`, then edit that. You need to at least set your Public IP address in `myIpAddr`, and your adapter IP if it is different from your public IP. If unsure, leave the `bindI` as `0.0.0.0`.
### RSA Keys
#### Your private / public keypair
You'll need to generate an RSA public and private keypair for your server and your proxy's clients for the proxy to work. You can use OpenSSL to do this.

First, change into the keys folder.
```
    cd ~/PSO2Proxy/proxy/keys
```

Generate the private key:

`openssl genpkey -out myKey.pem -algorithm rsa -pkeyopt rsa_keygen_bits:1024`

Generate a compatible publickey.blob for your clients:

`openssl rsa -in myKey.pem -outform MS\ PUBLICKEYBLOB -pubout -out publickey.blob`
#### SEGA's Public key
You'll ALSO need to import SEGA's RSA public keys from the PSO2 client. For instructions on how to get SEGAKey.blob, see [this wiki page](https://github.com/cyberkitsune/PSO2Proxy/wiki/Getting-SEGA's-RSA-Keys).

To convert SEGAKey.blob to SEGAKey.pem, use this OpenSSL command:

`openssl rsa -pubin -inform MS\ PUBLICKEYBLOB -in SEGAKey.blob -outform PEM -out SEGAKey.pem`
### Plugins
PSO2Proxy has several plugins that come bundled in to make the experience better. Most of them are disabed by default, with the exception of `LoginMessage` and `GlobalChat`. To disable a plugin that is not in the disabled folder, simply delete it.

If you would like to enable a plugin already in the disabled folder, use the following command to make symlinks so they get updated.
```
    cd ~/PSO2Proxy/proxy/plugins
    ln -s disabled/DisabledPluginName.py .
```
## Getting clients to connect
### Automatic configuration
For automatic configuration using PSO2Tweaker, simply enable WebAPI.py and point the tweaker to http://your.ip.addr.here:8080/config.json

To enable WebAPI...
```
    cd ~/PSO2Proxy/proxy/plugins
    ln -s disabled/WebAPI.py .
```
Be sure that publickey.blob is in your keys/ folder.
### Manual Mode
#### Rebind hosts file
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
#### Use your RSA keys
To get the proxy to decrypt the client's packets, place the publickey.blob you generated in the same folder as PSO2.exe, and rename the RSAKeyInjector.dll to ddraw.dll in that same folder. **If you use PSO2Tweaker to launch PSO2**, enable the item translation patch and rename ddraw.dll to rsainject.dll instead.

