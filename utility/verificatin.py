from utility.hash_util import hash_string_256, hash_block

from wallet import Wallet


class Verification:

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """Validate a proof of work number and see if it solves the puzzle algorithm (two leading 0s)

        Arguments:
            :transactions: The transactions of the block for which the proof is created.
            :last_hash: The previous block's hash which will be stored in the current block.
            :proof: The proof number we're testing.
        """
        ordered_transactions = [
            tx.to_ordered_dict()
            for tx in transactions
        ]
        guess = (str(ordered_transactions) +
                 str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        # print(f'guess_hash: {guess_hash}')

        return guess_hash[0:2] == '00'

    @classmethod
    def verify_chain(cls, blockchain):
        """ Verify the current blockchein and return True if it's valid. """
        # print('  verify_chain()')
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print(f'Proof of work is invalid! - {block.proof}')
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        """ Checks whether the sender has enough coins. """
        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        """ Verifies all open transactions. """
        return all([
            cls.verify_transaction(tx, get_balance, False)
            for tx in open_transactions
        ])
