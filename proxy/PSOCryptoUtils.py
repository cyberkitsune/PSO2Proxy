from Crypto.Cipher import ARC4, PKCS1_v1_5
from Crypto.PublicKey import RSA


class PSO2RC4(object):
    """docstring for PSO2RC4Decrypter"""

    def __init__(self, key):
        self.rc4key = key
        self.rc4de = ARC4.new(key)
        self.rc4en = ARC4.new(key)

    def decrypt(self, data):
        return self.rc4de.decrypt(data)

    def encrypt(self, data):
        return self.rc4en.encrypt(data)


class PSO2RSADecrypt(object):
    """docstring for PSO2RSADecrypt"""

    def __init__(self, private_key):
        try:
            key_data = open(private_key).read()
            self.key = RSA.importKey(key_data)
            print("[CryptoUtils] Loaded RSA decrypter from private_key '%s'." % (private_key,))
        except IOError:
            print("[CryptoUtils] Unable to load RSA decrypter from private key %s!" % private_key)

    def decrypt(self, data):
        cipher = PKCS1_v1_5.new(self.key)
        try:
            return cipher.decrypt(''.join(reversed(data)), None)  # For now
        except ValueError:
            log.msg("Message too large to decrypt")
            return None


class PSO2RSAEncrypt(object):
    """docstring for PSO2RSAEncrypt"""

    def __init__(self, pubkey):
        try:
            key_data = open(pubkey).read()
            self.key = RSA.importKey(key_data)
            print("[CryptoUtils] loaded RSA decrypter from pubkey '%s'." % (pubkey,))
        except IOError:
            print("[CryptoUtils] Unable to load RSA decrypter from public key %s!" % pubkey)

    def encrypt(self, data):
        cipher = PKCS1_v1_5.new(self.key)
        try:
            return ''.join(reversed(cipher.encrypt(data)))  # Because MICROSOFT
        except ValueError:
            log.msg("Message too large to encrypt")
            return None
