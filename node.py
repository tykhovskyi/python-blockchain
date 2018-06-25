from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from blockchain import Blockchain
from wallet import Wallet


app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def get_node_ui():
    return send_from_directory('ui', 'node.html')


@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving of keys failed!'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Loading of keys failed!'
        }
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message': 'Fetched balance successfully.',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading of balance failed!',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {'message': 'No wallet set up!'}
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': "Required data ('recipient' and 'amount') is missing!"
        }
        return jsonify(response), 400

    recipient = values['recipient']
    amount = values['amount']
    signature = wallet.sign_transaction(wallet.public_key,
                                        recipient,
                                        amount)
    success = blockchain.add_transaction(recipient,
                                         wallet.public_key,
                                         signature,
                                         amount)
    if success:
        response = {
            'message': 'Successfully added new transaction.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {'message': 'Adding of transaction failed!'}
        return jsonify(response), 500


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    request_json = request.get_json()
    if not request_json:
        response = {'message': 'No data found!'}
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(key in request_json for key in required):
        response = {'message': 'Some data is missing!'}
        return jsonify(response), 400

    success = blockchain.add_transaction(request_json['recipient'],
                                         request_json['sender'],
                                         request_json['signature'],
                                         request_json['amount'],
                                         is_receiving=True)
    if success:
        response = {'message': 'Successfully added new transaction.'}
        return jsonify(response), 201
    else:
        response = {'message': 'Adding of transaction failed!'}
        return jsonify(response), 500


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    request_json = request.get_json()
    if not request_json:
        response = {'message': 'No data found!'}
        return jsonify(response), 400
    if 'block' not in request_json:
        response = {'message': 'Some data is missing!'}
        return jsonify(response), 400
    
    block = request_json['block']
    if block['index'] == blockchain.get_last_index() + 1:
        blockchain.add_block(block)
    elif block['index'] > blockchain.get_last_index():
        pass
    else:
        response = {'message': 'Blockchain seems to be shorter, block not added!'}
        return jsonify(response), 409


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
            'block': dict_block,
            'funds': blockchain.get_balance()
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


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    response = {
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()

    if not values:
        response = {
            'message': 'No data attached!'
        }
        return jsonify(response), 400

    if 'node' not in values:
        response = {
            'message': 'No node data found!'
        }
        return jsonify(response), 400

    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added seccessfully.',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == None or node_url == '':
        response = {
            'message': 'No node found!'
        }
        return jsonify(response), 400

    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Node removed.',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port

    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)

    app.run(host='0.0.0.0', port=port)
