import binascii
from Crypto.PublicKey import RSA


class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def load_keys(self):
        pass

    def generate_keys(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()

        return (self.stringify_key(private_key), self.stringify_key(public_key))

    @staticmethod
    def stringify_key(key):
        return binascii.hexlify(key.exportKey(format='DER'))


# print('---test')

# key = RSA.generate(1024)
# private_key = key.export_key()
# # private_key_str = binascii.hexlify(key.exportKey(format='DER').decode('ascii'))
# private_key_str = binascii.hexlify(key.exportKey(format='DER'))
# print(private_key_str)
