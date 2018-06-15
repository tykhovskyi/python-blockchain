import binascii
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def save_keys(self):
        if self.public_key != None and self.private_key != None:
            try:
                with open('tmp_data/wallet.txt', mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
            except (IOError, IndexError):
                print('Saving wallet failed...')

    def load_keys(self):
        try:
            with open('tmp_data/wallet.txt', mode='r') as f:
                keys = f.readlines()
                self.public_key = keys[0][:-1]
                self.private_key = keys[1]
        except (IOError, IndexError):
            print('Loading wallet failed...')

    def generate_keys(self):
        key = RSA.generate(2048)
        private_key = key
        public_key = key.publickey()

        return (self.key_to_string(private_key), self.key_to_string(public_key))

    def sign_transaction(self, sender, recipient, amount):
        signer = pkcs1_15.new(self.string_to_key(self.private_key))
        h = SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))
        signature = signer.sign(h)

        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def string_to_key(str):
        return RSA.import_key(binascii.unhexlify(str))

    @staticmethod
    def key_to_string(key):
        return binascii.hexlify(key.exportKey(format='DER')).decode('ascii')


# print('---test')

# wallet = Wallet()
# wallet.create_keys()

# # private_key_str = wallet.public_key
# # public_key_str = wallet.public_key
# # print('private_key_str')
# # print(private_key_str)
# # print('public_key_str')
# # print(public_key_str)

# signature = wallet.sign_transaction('sender1', 'recipient1', 101)
# print(signature)
