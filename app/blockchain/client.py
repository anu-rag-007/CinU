import os
from dotenv import load_dotenv
from web3 import Web3
load_dotenv()

class BlockchainClient:
    def __init__(self):
        rpc_url = os.getenv(
            "POLYGON_RPC_URL"
        )

        private_key = os.getenv(
            "PRIVATE_KEY"
        )

        if not rpc_url:
            raise RuntimeError(
                "POLYGON_RPC_URL is missing from .env"
            )

        if not private_key:
            raise RuntimeError(
                "PRIVATE_KEY is missing from .env"
            )

        self.web3 = Web3(
            Web3.HTTPProvider(rpc_url)
        )

        if not self.web3.is_connected():
            raise RuntimeError(
                "Could not connect to Polygon Amoy"
            )

        self.private_key = private_key
        self.account = self.web3.eth.account.from_key(
            private_key
        )

        self.address = self.account.address
        print(f"Connected wallet: {self.address}")

    def get_balance(self):
        balance = self.web3.eth.get_balance(self.address)
        return self.web3.from_wei(balance,"ether")

    def store_hash(self, fingerprint: str):
        nonce = self.web3.eth.get_transaction_count(self.address)
        transaction = {
            "from": self.address,
            "to": self.address,
            "value": 0,
            "nonce": nonce,
            "chainId": self.web3.eth.chain_id,
            "gas": 30000,
            "gasPrice": self.web3.eth.gas_price,
            "data": bytes.fromhex(fingerprint),
        }

        signed_transaction = (
            self.web3.eth.account.sign_transaction(
                transaction,
                self.private_key,
            )
        )

        tx_hash = self.web3.eth.send_raw_transaction(
            signed_transaction.raw_transaction
        )

        return tx_hash.hex()

    def get_transaction(self, tx_hash: str):
        return self.web3.eth.get_transaction(tx_hash)
    
    def get_transaction_data(self, tx_hash: str):
        transaction = self.web3.eth.get_transaction(tx_hash)
        return transaction["input"].hex()