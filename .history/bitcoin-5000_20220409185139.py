from operator import contains
import wx
from bitcoinclass import Transaction,Wallet,Block,Blockchain
from flask import Flask, jsonify, request, render_template, redirect, url_for, send_file
from urllib.parse import urlparse
import json
import re
import requests
import io
app = Flask(__name__)

#Flask API
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    values = request.form
    
    # Check that the required fields are in the PoST'ed data
    required = ['recipient_address', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    
    #Create a new Transaction
    transaction = Transaction(myWallet.identity, values['recipient_address'], values[ 'amount'])
    transaction.add_signature(myWallet.sign_transaction(transaction))
    transaction_result = blockchain.add_new_transaction(transaction)
    
    if transaction_result:
        response = { 'message': 'Transaction will be added to Block '}
        return jsonify(response), 201
    else:
        response = {'message': 'Invalid Transaction! '}
        return jsonify(response), 406

@app.route( '/get_transactions' , methods=[ 'GET'])
def get_transactions():
    #Get transactions from transactions pool
    transactions = blockchain.unconfirmed_transactions
    response = {'transactions' : transactions}
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def last_ten_blocks():
    response = {
        'chain' : blockchain.chain[-10:],
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/fullchain', methods=['GET'])
def full_chain():
    response = {
    'chain' : json.dumps(blockchain.chain), 
    'length' : len(blockchain.chain),
    }
    return jsonify (response), 200

@app.route('/get_nodes', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {'nodes' : nodes}
    return jsonify(response), 200

@app.route('/register_node', methods=['PoST'])
def register_node():
    values = request.form
    node = values.get('node')
    com_port = values.get('com_port')
    if com_port is not None:
        blockchain.register_node(request.remote_addr + ":" + com_port)
        return "ok", 200
    if node is None and com_port is None:
        return "Error: Please supply a valid list of nodes", 400
    
    blockchain.register_node(node)
    node_list = requests.get('http://' + node + '/get_nodes')
    if node_list.status_code == 200:
        node_list = node_list.json()['nodes']
        for node in node_list:
            blockchain.register_node( node)
        
    for new_nodes in blockchain.nodes:
        requests.post( 'http://' + new_nodes + '/register_node' , data={'com_port':str(port)})

    replaced = blockchain.consensus()    
    if replaced:
        response ={
        'message' : 'Longer authoritative chain found from peers, replacing ours' ,
        'total_nodes ' : [node for node in blockchain.nodes]}
    else:
        response ={
        'message': 'New nodes have been added,but our chain is authoritative',
        'total_nodes' : [node for node in blockchain.nodes]
    }
    return jsonify(response), 201

@app.route('/consensus', methods=['GET'])
def consensus():
    replaced = blockchain.consensus()
    if replaced:
        response = {
            'message' : 'our chain was replaced', 
        }
    else:
        response = {
        'message ' : 'our chain is authoritative',
        }
    return jsonify(response), 200

@app.route('/mine', methods=[ 'GET'])
def mine():
    newblock = blockchain.mine(myWallet)
    for node in blockchain.nodes:
        requests.get('http://' + node + '/consensus' )
    response = {
        'index' : newblock.index,
        'transactions' : newblock.transactions,
        'timestamp' : newblock.timestamp,
        'nonce' : newblock.nonce,
        'hash' : newblock.hash,
        'previous_hash' : newblock.previous_hash
    }
    return jsonify( response), 200

@app.route('/import_key', methods=['POST'])
def import_key():
    f = request.files['file']
    blob = f.read()
    myWallet.import_key(blob)
    return 'key imported successfully'

@app.route('/export_key', methods=['GET'])
def export_key():
    blob = myWallet.export_key()
    return send_file(
        io.BytesIO(blob),
        mimetype='application/octet-stream',
        as_attachment = True,
        attachment_filename = "keyfile")

@app.route('/get_status')

@app.route('/')
def index():
    return render_template('homepage.html')

if __name__ == '__main__':
    myWallet = Wallet()
    blockchain = Blockchain()
    port = 5000
    app.run(host='127.0.0.1', port=port, debug = True)