from app.blockchain.client import BlockchainClient
from app.blockchain.verify import verify_record

def main():

    print("\n" + "=" * 60)
    print("              CIN-U BLOCKCHAIN VERIFY")
    print("=" * 60)

    tx_hash = input(
        "\nEnter Polygon transaction hash:\n> "
    ).strip()

    if not tx_hash:

        print(
            "\n❌ Transaction hash is required."
        )

        return

    blockchain = BlockchainClient()

    print(
        "\nReading transaction..."
    )

    transaction = (
        blockchain.get_transaction(
            tx_hash
        )
    )

    stored_fingerprint = (
        transaction["input"].hex()
    )

    print(
        "\n✓ Fingerprint retrieved "
        "from blockchain:"
    )

    print(
        f"  {stored_fingerprint}"
    )

    print(
        "\nNow enter the original record."
    )

    platform = input(
        "Platform: "
    ).strip()

    title = input(
        "Title: "
    ).strip()

    match_type = input(
        "Match type: "
    ).strip()

    content_hash = input(
        "Content SHA-256: "
    ).strip()

    record = {

        "platform": platform,

        "title": title,

        "match_type": match_type,

        "content_hash": content_hash,
    }

    print(
        "\nVerifying..."
    )

    valid = verify_record(
        record,
        stored_fingerprint
    )

    print(
        "\n" + "=" * 60
    )

    if valid:

        print(
            "                 ✅ VERIFIED"
        )

        print(
            "\nThe record produces the "
            "same fingerprint stored "
            "on Polygon Amoy."
        )

    else:

        print(
            "                 ❌ FAILED"
        )

        print(
            "\nThe record does not match "
            "the blockchain fingerprint."
        )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()