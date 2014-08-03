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
        key_data = open(private_key).read()
        self.key = RSA.importKey(key_data)
        print("[CryptoUtils] loaded RSA decrypter from private_key '%s'." % (private_key,))

    def decrypt(self, data):
        cipher = PKCS1_v1_5.new(self.key)
        return cipher.decrypt(''.join(reversed(data)), None)  # For now


class PSO2RSAEncrypt(object):
    """docstring for PSO2RSAEncrypt"""

    def __init__(self, pubkey):
        key_data = open(pubkey).read()
        self.key = RSA.importKey(key_data)
        print("[CryptoUtils] loaded RSA decrypter from pubkey '%s'." % (pubkey,))

    def encrypt(self, data):
        cipher = PKCS1_v1_5.new(self.key)
        return ''.join(reversed(cipher.encrypt(data)))  # Because MICROSOFT
