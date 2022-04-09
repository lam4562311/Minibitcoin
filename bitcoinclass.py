import Crypto 
import Crypto.Random
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA256
import binascii
import json
import re
from urllib.parse import urlparse
import requests
import datetime

class Transaction:          #Transaction
    def __init__(self, sender,recipient,value):
        self.sender = sender
        self.recipient = recipient
        self.value = value
    def to_dict(self):
        return ({'sender': self.sender , 'recipient': self.recipient, 'value': self.value})

    def add_signature(self, signature_):
        self.signature = signature_
    
    def verify_transaction_signature(self):
        if hasattr(self, 'signature'):
            public_key = RSA.importKey(binascii.unhexlify(self.sender))
            verifier = PKCS1_v1_5.new(public_key)
            h = SHA256.new(str(self.to_dict()).encode('utf8'))
            return verifier.verify(h, binascii.unhexlify(self.signature))
        else:
            return False
        
    
    def verify_sender_balance(self):
        if hasattr(self, 'sender') :
            balance = 0.0
            print(blockchain.chain) # debug
            for block_json in blockchain.chain: # 1: confirmed historical blocks
                block = json.loads(block_json)
                print("Block: " + json.dumps(block)) # debug
                if len(block["transactions"]) > 0:
                    for tx_json in block["transactions"]:
                        tx = json.loads(tx_json)
                        if tx["recipient"] == self.sender:
                            balance += float(tx["value"])
                        if tx["sender"] == self.sender:
                            balance -= float(tx["value"])
            
            if len(blockchain.unconfirmed_transactions) > 0: # 2: unconfirmed tx mempool
                for unconfimed_tx_json in blockchain.unconfirmed_transactions: 
                    unconfimed_tx = json.loads(unconfimed_tx_json)
                    if unconfimed_tx["recipient"] == self.sender:
                        balance += float(unconfimed_tx["value"])
                    if unconfimed_tx["sender"] == self.sender:
                        balance -= float(unconfimed_tx["value"])
                            
            print("Balance: " + str(balance) + " / sending: " + self.value) # debug
            if balance >= float(self.value):
                return True
        return False
            

    def to_json(self):
        return json.dumps( self.__dict__, sort_keys = False)


class Wallet:       #Wallet
    def __init__(self):
        random = Crypto.Random.new().read
        self._private_key = RSA.generate(1024,random)
        self._public_key = self._private_key.publickey()
        self.balance = 1000.0
    def sign_transaction(self, transaction: Transaction) :
        signer = PKCS1_v1_5.new(self._private_key)
        h = SHA256.new(str(transaction.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')

    def import_key(self, input_key):
        self._private_key = RSA.import_key(input_key)
        self._public_key = self._private_key.publickey()

    def export_key(self):
        return self._private_key.exportKey(format='DER')

    @property
    def identity(self):
        pubkey = binascii.hexlify( self._public_key.exportKey(format='DER'))
        return pubkey.decode('ascii')

    @property
    def private(self):
        private_key = binascii.hexlify( self._private_key.exportKey(format='DER'))
        return private_key.decode('ascii')
    
    def update_balance(self, value):
        self.balance = value
    
    def get_balance(self):
        return self.balance
class Block :       #Block
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = None
        self.nonce = 0
    def to_dict(self):
        return ({
            'index' : self.index,
            'transactions' : self.transactions,
            'timestamp' : self.timestamp,
            'previous_hash' : self.previous_hash,
            'nonce' : self.nonce}
        )
    def to_json(self):
        return json.dumps (self.__dict__)
    def compute_hash( self):
        return SHA256.new(str(self.to_dict()).encode()).hexdigest()


class Blockchain:       #Blockchain
    difficulty = 2
    nodes=set()
    
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block( self):
        genesis_block = Block(0, [], datetime.datetime.now()
                                .strftime("%m/%d/%Y, %H:%M:%S"),"0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block.to_json())
    def add_new_transaction(self, transaction: Transaction):
        if transaction.verify_transaction_signature() and transaction.verify_sender_balance():
            self.unconfirmed_transactions.append(transaction.to_json())
            return True
        else:
            return False

    def add_block( self, block, proof):

        previous_hash = self.last_block[ 'hash' ]

        if previous_hash != block.previous_hash:
            return False
        
        if not self.is_valid_proof(block, proof):
            return False
        
        block.hash = proof
        self.chain.append(block.to_json())
        return True

    def is_valid_proof(self, block, block_hash):

        return (block_hash.startswith( '0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    def proof_of_work(self, block ):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith( '0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash
    
    def mine(self, mywallet) :
        block_reward = Transaction( "Block_Reward" ,
                                    mywallet.identity, "5.0" ).to_json()
        self.unconfirmed_transactions.insert(0, block_reward)
        if not self.unconfirmed_transactions:
            return False

        new_block = Block(index=self.last_block['index'] + 1,
                            transactions=self.unconfirmed_transactions,
                            timestamp=datetime.datetime.now()
                            .strftime("%m/%d/%Y, %H:%M:%S"),
                            previous_hash=self.last_block['hash'])

        proof = self.proof_of_work(new_block)
        if self.add_block(new_block, proof):
            self.unconfirmed_transactions = []
            return new_block
        else:
            return False
    
    @property
    def last_block(self):
        return json.loads(self.chain[-1])
    
    def register_node( self, node_url):
        """
        Add a new node to the list of nodes
        """
        # checking node_url has valid format
        parsed_url = urlparse( node_url)
        if parsed_url.netloc:
            self.nodes.add( parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self,chain):
        #check if a bockchain is valid
        current_index = 0
        chain = json.loads(chain)
        while current_index < len(chain):
            block = json.loads(chain[ current_index])
            current_block = Block(block['index'],
                                  block['transactions'],
                                  block['timestamp'],
                                  block['previous_hash'],
                                  block['hash'],
                                  block['nonce'])
            if current_index + 1 < len(chain) :
                if current_block.compute_hash() != json.loads(chain[current_index + 1])[ 'previous_hash']:
                    return False
            if isinstance( current_block.transactions, list):
                for transaction in current_block.transactions:
                    transaction = json. loads(transaction)
                    if transaction['sender'] == 'Block_Reward':
                        continue
                    current_transaction = Transaction(transaction['sender'],
                                                      transaction['recipient'],
                                                      transaction['value'],
                                                      transaction['signature'])
                    if not current_transaction.verify_transaction_signature():
                        return False
                if not self.is_valid_proof(current_block, block['hash']):
                    return False
            current_index += 1
            
        return True


    def consensus(self) :
        """
        Resolve conflicts between blockchain's nodes
        by replacing our chain with the longest one in the network.
        """
        neighbours = self.nodes
        new_chain = None
        
        # We're only looking for chains longer than ours
        max_length = len(self.chain)
        
        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get( 'http://' + node + '/fullchain' )
            
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
            
            # Check if the length is longer and the chain is valid
            if length > max_length and self.valid_chain(chain):
                max_length = length
                new_chain = chain
            # Replace our chain if we discovered a new，valid chain longer than ours
            if new_chain:
                self.chain = json.loads(new_chain)
                return True
            return False

    def get_balance(self, address):
    #get the balance from the given address
        
        balance = 0.0
        if len(self.chain) <= 0:
            return balance
        for block_json in self.chain:
            block = json.loads(block_json)
            transactions = block['transactions']
            for transaction_json in transactions:
                transaction = json.loads(transaction_json)
                if transaction['sender'] == address:
                    balance -= (float(transaction['value']) + float(transaction['fee']))
                if transaction['recipient'] == address:
                    balance += float(transaction['value'])
        return balance