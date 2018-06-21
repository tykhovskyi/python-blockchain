from functools import reduce
import json
# import pickle

from block import Block
from transaction import Transaction
from utility.hash_util import hash_block
from utility.verificatin import Verification
from wallet import Wallet


# The reward we give to miners (for creating a new block)
MINING_REWARD = 10


class Blockchain:

    def __init__(self, public_key, node_id):
        genesis_block = Block(0, '', [], 0, 0)
        self.__chain = [genesis_block]
        self.__open_transactions = []
        self.__peer_nodes = set()
        self.public_key = public_key
        self.node_id = node_id
        self.load_data()

    def get_chain(self):
        return self.__chain[:]

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        """Initialize blockchain + open transactions data from a file."""
        try:
            with open('tmp_data/blockchain-{}.txt'.format(self.node_id), mode='r') as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [
                        Transaction(
                            tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
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
                self.__chain = updated_blockchain

                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions

                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            print('Handled exception...')

    def save_data(self):
        """Save blockchain + open transactions snapshot to a file."""
        try:
            with open('tmp_data/blockchain-{}.txt'.format(self.node_id), mode='w') as f:
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
                        for b in self.__chain
                    ]
                ]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [
                    tx.__dict__
                    for tx in self.__open_transactions
                ]
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
        except IOError:
            print('Saving failed!')

    def proof_of_work(self):
        """Generate a proof of work for the open transactions, the hash of the previous block and a random number (which is guessed until it fits)."""
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0

        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1

        return proof

    def get_balance(self):
        """Calculate and return the balance for a participant."""
        if self.public_key == None:
            return None

        participant = self.public_key
        # get all transactions from blockchain
        # where participant is sender
        tx_sender = [
            [
                tx.amount
                for tx in block.transactions
                if tx.sender == participant
            ]
            for block in self.__chain
        ]
        # get all transactions from open transactions
        # where participant is sender
        open_tx_sender = [
            tx.amount
            for tx in self.__open_transactions
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
            for block in self.__chain
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
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """ Append a new value as well as the last blockchain value to the blockchain.

        Arguments:
            :sender: The sender of the coins.
            :recipient: The recipient of the coins.
            :signature: The signature of the transaction.
            :amount: The amount of coins sent with the transaction (default = 1.0)
        """
        if self.public_key == None:
            return False

        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        """ Create a new block and add open transactions to it. """
        if self.public_key == None:
            return None

        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction(
            'MINING', self.public_key, '', MINING_REWARD)

        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)

        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, proof)

        self.__chain.append(block)

        self.__open_transactions = []
        self.save_data()

        return block

    def add_peer_node(self, node):
        """Adds a new node to the peer node set.
        
        Arguments:
            :node: The node URL which should be added.
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        """Removes a node from the peer node set.
        
        Arguments:
            :node: The node URL which should be removeded.
        """
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        """Return a list of all connected peer nodes."""
        return list(self.__peer_nodes)
