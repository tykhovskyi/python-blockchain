from functools import reduce
import json
# import pickle

from block import Block
from hash_util import hash_block
from transaction import Transaction
from verificatin import Verification


# The reward we give to miners (for creating a new block)
MINING_REWARD = 10
data_file_path = 'tmp_data/blockchain.txt'


class Blockchain:

    def __init__(self, hosting_node_id):
        genesis_block = Block(0, '', [], 0, 0)
        self.chain = [genesis_block]
        self.open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id

    def load_data(self):
        """Initialize blockchain + open transactions data from a file."""
        try:
            with open(data_file_path, mode='r') as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [
                        Transaction(
                            tx['sender'], tx['recipient'], tx['amount'])
                        for tx in block['transactions']
                    ]
                    updated_block = Block(
                        block['index'],
                        block['previous_hash'],
                        converted_tx,
                        block['proof'],
                        block['timestamp']
                    )
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain

                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx['sender'], tx['recipient'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.open_transactions = updated_transactions
        except (IOError, IndexError):
            print('Handled exception...')

    def save_data(self):
        """Save blockchain + open transactions snapshot to a file."""
        try:
            with open(data_file_path, mode='w') as f:
                saveable_chain = [
                    block.__dict__
                    for block in [
                        Block(
                            b.index,
                            b.previous_hash,
                            [tx.__dict__ for tx in b.transactions],
                            b.proof,
                            b.timestamp
                        )
                        for b in self.chain
                    ]
                ]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [
                    tx.__dict__
                    for tx in self.open_transactions
                ]
                f.write(json.dumps(saveable_tx))
        except IOError:
            print('Saving failed!')

    def proof_of_work(self):
        """Generate a proof of work for the open transactions, the hash of the previous block and a random number (which is guessed until it fits)."""
        last_block = self.chain[-1]
        last_hash = hash_block(last_block)
        proof = 0

        verifier = Verification()
        while not verifier.valid_proof(self.open_transactions, last_hash, proof):
            proof += 1

        return proof

    def get_balance(self):
        """Calculate and return the balance for a participant."""
        participant = self.hosting_node
        # get all transactions from blockchain
        # where participant is sender
        tx_sender = [
            [
                tx.amount
                for tx in block.transactions
                if tx.sender == participant
            ]
            for block in self.chain
        ]
        # get all transactions from open transactions
        # where participant is sender
        open_tx_sender = [
            tx.amount
            for tx in self.open_transactions
            if tx.sender == participant
        ]
        tx_sender.append(open_tx_sender)
        amount_sent = reduce(
            lambda tx_sum, tx_amt:
                tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
            tx_sender,
            0
        )

        # get all transactions from blockchain
        # where participant is recipient
        tx_recipient = [
            [
                tx.amount
                for tx in block.transactions
                if tx.recipient == participant
            ]
            for block in self.chain
        ]
        amount_received = reduce(
            lambda tx_sum, tx_amt:
                tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
            tx_recipient,
            0
        )

        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain. """
        if len(self.chain) < 1:
            return None
        return self.chain[-1]

    def add_transaction(self, recipient, sender, amount=1.0):
        """ Append a new value as well as the last blockchain value to the blockchain.

        Arguments:
            :sender: The sender of the coins.
            :recipient: The recipient of the coins.
            :amount: The amount of coins sent with the transaction (default = 1.0)
        """
        transaction = Transaction(sender, recipient, amount)
        verifier = Verification()
        if verifier.verify_transaction(transaction, self.get_balance):
            self.open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        """ Create a new block and add open transactions to it. """
        last_block = self.chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction('MINING', self.hosting_node, MINING_REWARD)

        copied_transactions = self.open_transactions[:]
        copied_transactions.append(reward_transaction)

        block = Block(len(self.chain), hashed_block,
                      copied_transactions, proof)
        self.chain.append(block)

        self.open_transactions = []
        self.save_data()

        return True
