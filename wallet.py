import binascii
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from transaction import Transaction


class Wallet:
    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None
        self.node_id = node_id

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def save_keys(self):
        if self.public_key != None and self.private_key != None:
            try:
                with open('tmp_data/wallet-{}.txt'.format(self.node_id), mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
                    return True
            except (IOError, IndexError):
                print('Saving wallet failed...')
                return False

    def load_keys(self):
        try:
            with open('tmp_data/wallet-{}.txt'.format(self.node_id), mode='r') as f:
                keys = f.readlines()
                self.public_key = keys[0][:-1]
                self.private_key = keys[1]
            return True
        except (IOError, IndexError):
            print('Loading wallet failed...')
            return False

    def generate_keys(self):
        key = RSA.generate(2048)
        private_key = key
        public_key = key.publickey()

        return (Wallet.__key_to_string(private_key), Wallet.__key_to_string(public_key))

    def sign_transaction(self, sender, recipient, amount):
        signer = pkcs1_15.new(Wallet.__string_to_key(self.private_key))
        h = Wallet.__to_hash(sender, recipient, amount)
        signature = signer.sign(h)

        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction(transaction):
        if transaction.sender == 'MINING':
            return True

        public_key = Wallet.__string_to_key(transaction.sender)
        verifier = pkcs1_15.new(public_key)
        h = Wallet.__to_hash(transaction.sender,
                             transaction.recipient,
                             transaction.amount)

        try:
            verifier.verify(h, binascii.unhexlify(transaction.signature))
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def __to_hash(sender, recipient, amount):
        return SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))

    @staticmethod
    def __string_to_key(str):
        return RSA.import_key(binascii.unhexlify(str))

    @staticmethod
    def __key_to_string(key):
        return binascii.hexlify(key.exportKey(format='DER')).decode('ascii')


# print('---test')

# wallet_sender = Wallet()
# wallet_sender.create_keys()
# wallet_recipient = Wallet()
# wallet_recipient.create_keys()

# # private_key_str = wallet.public_key
# # public_key_str = wallet.public_key
# # print('private_key_str')
# # print(private_key_str)
# # print('public_key_str')
# # print(public_key_str)

# sender = wallet_sender.public_key
# recipient = wallet_recipient.public_key

# signature = wallet_sender.sign_transaction(sender, recipient, 101)
# tx = Transaction(sender, recipient, signature, 101)
# is_valid = Wallet.verify_transaction(tx)
# print(is_valid)
