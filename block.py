from time import time

from transaction import Transaction
from utility.printable import Printable


class Block(Printable):

    def __init__(self, index, previous_hash, transactions, proof, time=time()):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time
        self.transactions = transactions
        self.proof = proof

    @staticmethod
    def from_dictionary(block):
        """Returns new instance of Block class converted form a dictionary."""
        transactions = [
            Transaction(tx['sender'],
                        tx['recipient'],
                        tx['signature'],
                        tx['amount'])
            for tx in block['transactions']
        ]
        return Block(block['index'],
                     block['previous_hash'],
                     transactions,
                     block['proof'],
                     block['timestamp'],)
