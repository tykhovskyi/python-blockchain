from flask import Flask, jsonify
from flask_cors import CORS

from blockchain import Blockchain
from wallet import Wallet


app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app)


@app.route('/', methods=['GET'])
def get_ui():
    return 'This works!'


@app.route('/mine', methods=['POST'])
def mine():
    mined_block = blockchain.mine_block()
    if mined_block != None:
        dict_block = mined_block.__dict__.copy()
        dict_block['transactions'] = [
            tx.__dict__
            for tx in dict_block['transactions']
        ]
        response = {
            'message': 'Block added successfully.',
            'block': dict_block
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Mining is failed!',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.get_chain()
    dict_chain = [
        block.__dict__.copy()
        for block in chain_snapshot
    ]
    for dict_block in dict_chain:
        dict_block['transactions'] = [
            tx.__dict__
            for tx in dict_block['transactions']
        ]
        
    return jsonify(dict_chain), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
