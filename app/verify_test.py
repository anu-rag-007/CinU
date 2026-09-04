from blockchain.client import BlockchainClient
from blockchain.verify import verify_record

def main():
    print("\n" + "=" * 60)
    print("             ACCISENSE BLOCKCHAIN VERIFY")
    print("=" * 60)

    tx_hash = input("\nEnter Polygon transaction hash: ").strip()
    if not tx_hash:
        print("❌ Transaction hash is required.")
        return

    blockchain = BlockchainClient()
    print("\nFetching blockchain transaction...")
    transaction = blockchain.web3.eth.get_transaction(
        tx_hash
    )

    on_chain_data = transaction["input"]
    if isinstance(on_chain_data, bytes):
        on_chain_data = on_chain_data.hex()

    on_chain_fingerprint = on_chain_data.removeprefix("0x")

    print("\n✓ Transaction found")
    print(f"  Block: {transaction['blockNumber']}")
    print(f"  On-chain fingerprint:")
    print(f"  {on_chain_fingerprint}")

    print("\nNow enter the original record.")

    platform = input("Platform: ").strip()
    title = input("Title: ").strip()
    url = input("URL: ").strip()
    match_type = input("Match type: ").strip()

    record = {
        "platform": platform,
        "title": title,
        "url": url,
        "match_type": match_type,
    }

    print("\nVerifying record...")

    verified = verify_record(
        record,
        on_chain_fingerprint,
    )

    print("\n" + "=" * 60)

    if verified:
        print("             ✅ VERIFIED")
        print("=" * 60)
        print("\nThe record fingerprint matches")
        print("the fingerprint recorded on Polygon Amoy.")
    else:
        print("             ❌ NOT VERIFIED")
        print("=" * 60)
        print("\nThe record does NOT match")
        print("the fingerprint recorded on Polygon Amoy.")


if __name__ == "__main__":
    main()