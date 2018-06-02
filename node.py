from uuid import uuid4

from blockchain import Blockchain
from verificatin import Verification


class Node:

    def __init__(self):
        # self.id = str(uuid4())
        self.id = 'Yurii'
        self.blockchain = Blockchain(self.id)

    def get_transaction_value(self):
        """ Returns the input of the user (a new transaction amount) as a float. """
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Your transaction amount please: '))
        return tx_recipient, tx_amount

    def get_user_choice(self):
        """Prompts the user for its choice and return it."""
        return input('Your choice: ')

    def print_blockchain_elements(self):
        """ Output the blockchain list to the console. """
        for block in self.blockchain.chain:
            print('Outputting Block')
            print(block)
        else:
            print('-' * 20)

    def listen_for_input(self):
        while True:
            print('\nPlease choose')
            print('1: Add a new transaction vallue')
            print('2: Mine a new block')
            print('3: Output the blockchain blocks')
            print('4: Check transaction validity')
            print('q: Quit')
            user_choice = self.get_user_choice()
            print('')

            verifier = Verification()
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print('\nTransaction added.')
                else:
                    print('\nTransaction failed!')
                print(self.blockchain.open_transactions)

            elif user_choice == '2':
                self.blockchain.mine_block()

            elif user_choice == '3':
                self.print_blockchain_elements()

            elif user_choice == '4':
                if verifier.verify_transactions(self.blockchain.open_transactions, self.blockchain.get_balance):
                    print('All transactions are valid')
                else:
                    print('There are invalid transactions!')

            elif user_choice == 'q':
                break

            else:
                print('Input was invalid, please pick a value from the list!')

            if not verifier.verify_chain(self.blockchain.chain):
                print('Invalid blockchain!')
                break
            print('Balance of {}: {:6.2f}'.format(
                self.id, self.blockchain.get_balance()))

        print('Done!')


node = Node()
node.listen_for_input()
