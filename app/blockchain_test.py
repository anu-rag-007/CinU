from blockchain.client import BlockchainClient
from blockchain.fingerprint import create_fingerprint


def main():

    print("\n" + "=" * 60)
    print("             POLYGON BLOCKCHAIN TEST")
    print("=" * 60)

    # Connect to Polygon Amoy
    client = BlockchainClient()

    print(f"\n✓ Connected to Polygon")
    print(f"  Wallet: {client.address}")
    print(f"  Chain ID: {client.web3.eth.chain_id}")

    # Check balance
    balance = client.get_balance()

    print(f"  Balance: {balance} POL")

    # Create test record
    test_record = {
        "platform": "LinkedIn",
        "title": "Test AcciSense Record",
        "url": "https://example.com/test",
        "match_type": "exact_match",
    }

    # Generate fingerprint
    fingerprint = create_fingerprint(test_record)

    print("\nCanonical record:")
    print(test_record)

    print("\nSHA-256 fingerprint:")
    print(f"  {fingerprint}")

    # Store fingerprint on Polygon
    print("\nSending transaction...")

    tx_hash = client.store_hash(fingerprint)

    print("\n✓ Transaction submitted!")
    print(f"  TX Hash: {tx_hash}")

    # Wait for confirmation
    print("\nWaiting for confirmation...")

    receipt = client.web3.eth.wait_for_transaction_receipt(
        tx_hash,
        timeout=120,
    )

    print("\n" + "=" * 60)
    print("             TRANSACTION CONFIRMED")
    print("=" * 60)

    print(f"\n✓ Status: {receipt.status}")
    print(f"✓ Block: {receipt.blockNumber}")
    print(f"✓ Transaction Hash:")
    print(f"  {tx_hash}")

    print("\nPolygon Amoy Explorer:")
    print(f"  https://amoy.polygonscan.com/tx/{tx_hash}")


if __name__ == "__main__":
    main()