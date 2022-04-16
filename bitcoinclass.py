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
        self.rate = 0.012
        if(sender=='Block_Reward' or sender=='interest'):
            self.fee = str(0)
        else:
            self.fee = str(float(self.value)*float(self.rate))

    def to_dict(self):
        return ({'sender': self.sender , 'recipient': self.recipient, 'value': self.value, 'fee': self.fee})

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
        
    
    def verify_sender_balance(self, blockchain):
        # Remember to make sure the unconfimred tx pool is in-sync with other nodes
        if hasattr(self, 'sender') :
            mixed_balance = 0.0
            print(blockchain.chain) # debug
            
            mixed_balance += blockchain.get_confirmed_balance(self.sender)
            mixed_balance += blockchain.get_unconfirmed_balance(self.sender)
                            
            print("Balance: " + str(mixed_balance) + " / sending: " + self.value + " (Plus fee: " + self.fee + ")") # debug
            if mixed_balance >= (float(self.value)+float(self.fee)):
                return True
        return False
            

    def to_json(self):
        return json.dumps( self.__dict__, sort_keys = False)


class Wallet:       #Wallet
    def __init__(self):
        random = Crypto.Random.new().read
        self._private_key = RSA.generate(1024,random)
        self._public_key = self._private_key.publickey()
        self.balance = 0.0
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
    def __init__(self, index, transactions, timestamp, previous_hash, difficulty):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = None
        self.nonce = 0
        self.difficulty = difficulty
    def to_dict(self):
        return ({
            'index' : self.index,
            'transactions' : self.transactions,
            'timestamp' : self.timestamp,
            'previous_hash' : self.previous_hash,
            'nonce' : self.nonce,
            'difficulty': self.difficulty}
        )
    def to_json(self):
        return json.dumps (self.__dict__)
    def compute_hash( self):
        return SHA256.new(str(self.to_dict()).encode()).hexdigest()


class Blockchain:       #Blockchain
    
    nodes=set()
    
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.interest_rate = 0.012
        self.create_genesis_block()
        self.difficulty_info = {'difficulty':3,
                                'accumulated_blocks_length':len(self.chain),
                                'previous_time_spent': None,
                                'current_time_spent': 0,
                                'timestamp': datetime.datetime.now()}

    def create_genesis_block( self):
        difficulty = 3
        genesis_block = Block(0, [], datetime.datetime.now()
                                .strftime("%m/%d/%Y, %H:%M:%S"),"0", difficulty)
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block.to_json())

    def add_new_transaction(self, transaction: Transaction):
        if transaction.verify_transaction_signature() and transaction.verify_sender_balance(self):
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

        return (block_hash.startswith( '0' * block.difficulty) and
                block_hash == block.compute_hash())

    def proof_of_work(self, block ):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith( '0' * block.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash
    
    def mine(self, mywallet) :
        init = datetime.datetime.now()
        
        transaction_num = len(self.chain)
        if (transaction_num %10 == 0 and transaction_num):
            address_list = self.get_address_list()
            interest_list = self.interest(address_list)
            if len(interest_list):
                for item in interest_list:
                    self.unconfirmed_transactions.append(item.to_json())
        
        block_reward = Transaction( "Block_Reward" ,
                                    mywallet.identity, "5.0" ).to_json()
        self.unconfirmed_transactions.insert(0, block_reward)

        self.boardcast_transactions()

        if not self.unconfirmed_transactions:
            return False

        new_block = Block(index=self.last_block['index'] + 1,
                            transactions=self.unconfirmed_transactions,
                            timestamp=datetime.datetime.now()
                            .strftime("%m/%d/%Y, %H:%M:%S"),
                            previous_hash=self.last_block['hash'],
                            difficulty=self.difficulty_info['difficulty'])

        proof = self.proof_of_work(new_block)
        if self.add_block(new_block, proof):
            self.unconfirmed_transactions = []
            
            now = datetime.datetime.now()
            self.difficulty_info['accumulated_blocks_length'] = len(self.chain)
            self.difficulty_info['current_time_spent'] += (now - init).total_seconds()
            self.difficulty_info['timestamp'] = now
            
            mywallet.balance = self.get_confirmed_balance(mywallet.identity)

            for node in self.nodes:
                consensus = requests.get('http://' + node + '/consensus')
                print("Updating node " + node + ": " + (consensus.json()['message'] if consensus.status_code == 200 else ("ERROR: " + str(consensus.status_code))))
                

            for node in self.nodes:
                requests.put('http://' + node + '/clear_transactions')

            self.difficulty_calculation()
            
            for node in self.nodes:
                requests.get('http://' + node + '/sync_difficulty_info')
            self.sync_difficulty()

            
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

    def consensus(self):
        # """
        # Resolve conflicts between blockchain's nodes
        # by replacing our chain with the longest one in the network.
        # """
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

    
    def valid_chain(self,chain):
        #check if a bockchain is valid
        current_index = 0
        chain = json.loads(chain)
        while current_index < len(chain):
            block = json.loads(chain[current_index])
            current_block = Block(block['index'],
                                  block['transactions'],
                                  block['timestamp'],
                                  block['previous_hash'],
                                  block['difficulty'])
            current_block.hash =  block['hash']
            current_block.nonce=  block['nonce']
            if current_index + 1 < len(chain):
                if current_block.compute_hash() != json.loads(chain[current_index + 1])['previous_hash']:
                    return False
            if isinstance(current_block.transactions, list):
                for transaction in current_block.transactions:
                    transaction = json.loads(transaction)
                    if transaction['sender'] == 'Block_Reward' or transaction['sender'] == 'interest':
                        continue
                    current_transaction = Transaction(transaction['sender'],
                                                      transaction['recipient'],
                                                      transaction['value'])
                    current_transaction.add_signature(transaction['signature'])
                    if not current_transaction.verify_transaction_signature():
                        return False
                    if not self.is_valid_proof(current_block, block['hash']):
                        return False
            current_index += 1
            
        return True
    
    
    def get_confirmed_balance(self, address):        
        balance = 0.0
        if not len(self.chain):
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

    def get_unconfirmed_balance(self, address):
        unconfirmed_balance = 0.0

        if len(self.unconfirmed_transactions) <= 0:
            return unconfirmed_balance
        
        for unconfimed_tx_json in self.unconfirmed_transactions:
            unconfimed_tx = json.loads(unconfimed_tx_json)
            if unconfimed_tx['sender'] == address:
                unconfirmed_balance -= (float(unconfimed_tx['value']) + float(unconfimed_tx['fee']))
            if unconfimed_tx['recipient'] == address:
                unconfirmed_balance += float(unconfimed_tx['value'])
        
        return unconfirmed_balance
    
    def boardcast_transactions(self):
        nodes = [node for node in self.nodes]
        for node in nodes:
            response = requests.get('http://'+ node +'/get_transactions')
            if response.status_code == 200:
                t = Transaction(response.json()['transactions'])
                for it in t:
                    self.add_new_transaction(it)
        return True

    def get_address_list(self):
        address_list = []
        for item in self.chain:
            block = json.loads(item)
            transactions = block['transactions']
            for it in transactions:
                transaction = json.loads(it)
                if transaction['sender'] not in address_list and transaction['sender'] !='Block_Reward' and transaction['sender'] !='interest':
                    address_list.append(transaction['sender'])
                if transaction['recipient'] not in address_list:
                    address_list.append(transaction['recipient'])
        return address_list

    def interest(self, address_list):
        interest_list = []
        if not len(address_list):
            return interest_list
        for item in address_list:
            cur_balance = self.get_confirmed_balance(item)
            interest = self.interest_rate * cur_balance
            interest_list.append(Transaction("interest",item, interest))
        return interest_list

    def sync_difficulty(self,address = ""):
        record_list=[]
        timestamp_list =[]

        if len(address) > 0:
            response = requests.get('http://' + address + '/difficulty_info')
            if response.status_code == 200:
                record = response.json()
                record_list.append(record)
                timestamp_list.append(record['timestamp'])
        else: # local
            record = self.difficulty_info
            record_list.append(record)
            timestamp_list.append(str(record['timestamp']))
        
        for node in self.nodes:
            response = requests.get('http://' + node + '/difficulty_info')
            if response.status_code == 200:
                record = response.json()
                record_list.append(record)
                timestamp_list.append(record['timestamp'])
        
        latest_record = record_list[timestamp_list.index(max(timestamp_list))]
        self.difficulty_info = latest_record
        return True
    
    def difficulty_calculation(self,address = ""):
        if len(address) > 0: 
            response = (requests.get('http://' + address + '/difficulty_info')).json()
        else: # local
            response = self.difficulty_info

        spent_time_percent=None
        if response['accumulated_blocks_length'] % 5 == 0:
            if self.difficulty_info['previous_time_spent'] == None:
                self.difficulty_info['difficulty'] = 3
            else:
                time_difference = self.difficulty_info['current_time_spent'] - self.difficulty_info['previous_time_spent']
                spent_time_percent = time_difference / self.difficulty_info['previous_time_spent']
                
                if abs(spent_time_percent) <= 5 and self.difficulty_info['difficulty'] <= 5:
                    self.difficulty_info['difficulty'] += 1
                elif abs(spent_time_percent) > 25 and (self.difficulty_info['difficulty'] >= 1):
                    self.difficulty_info['difficulty'] -= 1
            self.difficulty_info['previous_time_spent'] = response['current_time_spent']
            self.difficulty_info['current_time_spent'] = 0
            self.difficulty_info['timestamp'] = response['timestamp']
            return spent_time_percent

                