from functools import reduce
import json
import hashlib as hl
import pickle

from block import Block
from hash_util import hash_string_256, hash_block
from transaction import Transaction

MINING_REWARD = 10

blockchain = []
open_transactions = []
owner = 'Yurii'
participants = {owner}
data_file_path = 'tmp_data/blockchain.txt'


def initialize_new_blockchain():
    global blockchain
    global open_transactions
    genesis_block = Block(0, '', [], 0, 0)
    blockchain = [genesis_block]
    open_transactions = []


def load_data():
    try:
        with open(data_file_path, mode='r') as f:
            global blockchain
            global open_transactions

            file_content = f.readlines()
            global blockchain
            blockchain = json.loads(file_content[0][:-1])
            updated_blockchain = []
            for block in blockchain:
                converted_tx = [
                    Transaction(tx['sender'], tx['recipient'], tx['amount'])
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
            blockchain = updated_blockchain

            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transactions:
                updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                updated_transactions.append(updated_transaction)
            open_transactions = updated_transactions
    except (IOError, IndexError):
        initialize_new_blockchain()


load_data()


def save_data():
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
                    for b in blockchain
                ]
            ]
            f.write(json.dumps(saveable_chain))
            f.write('\n')
            saveable_tx = [
                tx.__dict__
                for tx in open_transactions
            ]
            f.write(json.dumps(saveable_tx))
    except IOError:
        print('Saving failed!')


def valid_proof(transactions, last_hash, proof):
    ordered_transactions = [
        tx.to_ordered_dict()
        for tx in transactions
    ]
    guess = (str(ordered_transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    print(f'guess_hash: {guess_hash}')

    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0

    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1

    return proof


def get_balance(participant):
    # get all transactions from blockchain
    # where participant is sender
    tx_sender = [
        [
            tx.amount
            for tx in block.transactions
            if tx.sender == participant
        ]
        for block in blockchain
    ]
    # get all transactions from open transactions
    # where participant is sender
    open_tx_sender = [
        tx.amount
        for tx in open_transactions
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
        for block in blockchain
    ]
    amount_received = reduce(
        lambda tx_sum, tx_amt:
            tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
        tx_recipient,
        0
    )

    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_chain():
    print('  verify_chain()')
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block.previous_hash != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            print(f'Proof of work is invalid! - {block.proof}')
            return False
    return True


def verify_transaction(transaction):
    """ Checks whether the sender has enough coins. """
    sender_balance = get_balance(transaction.sender)
    return sender_balance >= transaction.amount


def add_transaction(recipient, sender=owner, amount=1.0):
    transaction = Transaction(sender, recipient, amount)
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        save_data()
        return True
    return False


def mine_block():
    """ Create a new block and add open transactions to it. """
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    reward_transaction = Transaction('MINING', owner, MINING_REWARD)
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = Block(len(blockchain), hashed_block, copied_transactions, proof)
    blockchain.append(block)
    return True


def get_transaction_value():
    """ Returns the input of the user (a new transaction amount) as a float. """
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Your transaction amount please: '))
    return tx_recipient, tx_amount


def get_user_choice():
    return input('Your choice: ')


def print_blockchain_elements():
    """ Output the blockchain list to the console. """
    for block in blockchain:
        print('Outputting Block')
        print(block)
    else:
        print('-' * 20)


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


while True:
    print('\nPlease choose')
    print('1: Add a new transaction vallue')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('4: Output participants')
    print('5: Check transaction validity')
    print('q: Quit')
    user_choice = get_user_choice()
    print('')

    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print('\nTransaction added.')
        else:
            print('\nTransaction failed!')
        print(open_transactions)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid')
        else:
            print('There are invalid transactions!')
    elif user_choice == 'q':
        break
    else:
        print('Input was invalid, please pick a value from the list!')

    if not verify_chain():
        print('Invalid blockchain!')
        break
    print('Balance of {}: {:6.2f}'.format(owner, get_balance('Yurii')))

print('Done!')
