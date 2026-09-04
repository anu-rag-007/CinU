import sys
from pathlib import Path

from app.blockchain.client import BlockchainClient
from app.blockchain.storage import load_record
from app.blockchain.fingerprint import create_fingerprint
from app.blockchain.content_hash import sha256_file


def get_transaction_fingerprint(blockchain, tx_hash):
    transaction = blockchain.get_transaction(tx_hash)

    input_data = transaction["input"]

    if hasattr(input_data, "hex"):
        stored_fingerprint = input_data.hex()
    else:
        stored_fingerprint = str(input_data)

    if stored_fingerprint.startswith("0x"):
        stored_fingerprint = stored_fingerprint[2:]

    return stored_fingerprint.lower()


def main():

    project_root = Path(__file__).resolve().parent.parent

    if len(sys.argv) != 2:
        print("\nUsage:")
        print("  python -m app.verify <TX_HASH>")
        return

    tx_hash = sys.argv[1].strip()

    if not tx_hash:
        print("\n❌ Transaction hash is required.")
        return

    print("\n" + "=" * 70)
    print("                    CIN-U VERIFY")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. LOAD LOCAL RECORD
    # ---------------------------------------------------------

    record_path = (
        project_root
        / "output"
        / "records"
        / f"{tx_hash}.json"
    )

    print("\n[1/6] Loading CIN-U record...")

    try:
        saved_data = load_record(str(record_path))
    except FileNotFoundError:
        print("\n❌ No local verification record exists.")
        print(f"\nExpected:")
        print(f"  {record_path}")
        return

    record = saved_data["record"]
    saved_fingerprint = saved_data["fingerprint"]

    print("✓ Local record loaded")

    # ---------------------------------------------------------
    # 2. CONNECT TO BLOCKCHAIN
    # ---------------------------------------------------------

    print("\n[2/6] Connecting to Polygon Amoy...")

    try:
        blockchain = BlockchainClient()
    except Exception as error:
        print("\n❌ Blockchain connection failed:")
        print(f"  {error}")
        return

    print("✓ Connected to Polygon Amoy")

    # ---------------------------------------------------------
    # 3. READ BLOCKCHAIN
    # ---------------------------------------------------------

    print("\n[3/6] Reading blockchain transaction...")

    try:
        stored_fingerprint = get_transaction_fingerprint(
            blockchain,
            tx_hash
        )
    except Exception as error:
        print("\n❌ Could not read transaction:")
        print(f"  {error}")
        return

    print("✓ Blockchain fingerprint retrieved")

    print("\n  On-chain fingerprint:")
    print(f"  {stored_fingerprint}")

    # ---------------------------------------------------------
    # 4. INDEPENDENTLY HASH DISCOVERED CONTENT
    # ---------------------------------------------------------

    print("\n[4/6] Re-hashing discovered content...")

    content_path = (
        project_root
        / "output"
        / "discovered_content.jpg"
    )

    if not content_path.exists():
        print("\n❌ Discovered content is missing.")
        print(f"  Expected: {content_path}")
        return

    try:
        actual_content_hash = sha256_file(
            str(content_path)
        )
    except Exception as error:
        print("\n❌ Could not hash discovered content:")
        print(f"  {error}")
        return

    recorded_content_hash = record.get("content_hash")

    print("\n  Recorded content hash:")
    print(f"  {recorded_content_hash}")

    print("\n  Actual content hash:")
    print(f"  {actual_content_hash}")

    content_match = (
        recorded_content_hash is not None
        and actual_content_hash.lower()
        == recorded_content_hash.lower()
    )

    if content_match:
        print("\n✓ Content integrity verified")
    else:
        print("\n❌ Content integrity FAILED")
        print("\nThe discovered content has changed since recording.")
        return

    # ---------------------------------------------------------
    # 5. RECREATE RECORD FINGERPRINT
    # ---------------------------------------------------------

    print("\n[5/6] Recalculating record fingerprint...")

    calculated_fingerprint = create_fingerprint(record)

    print("\n  Local record fingerprint:")
    print(f"  {calculated_fingerprint}")

    local_record_match = (
        calculated_fingerprint.lower()
        == saved_fingerprint.lower()
    )

    if local_record_match:
        print("\n✓ Local record integrity verified")
    else:
        print("\n❌ Local record integrity FAILED")
        return

    # ---------------------------------------------------------
    # 6. COMPARE WITH BLOCKCHAIN
    # ---------------------------------------------------------

    print("\n[6/6] Comparing with Polygon Amoy...")

    blockchain_match = (
        stored_fingerprint.lower()
        == calculated_fingerprint.lower()
    )

    print("\n" + "=" * 70)

    if blockchain_match:
        print("                    ✅ VERIFIED")
        print("=" * 70)

        print("\nCIN-U verification successful.")

        print("\nVerification checks:")

        print("  ✓ Content file matches recorded SHA-256")
        print("  ✓ Local record fingerprint is valid")
        print("  ✓ Local fingerprint matches Polygon Amoy")
        print("  ✓ Blockchain record is intact")

        print("\nRecord:")

        for key, value in record.items():
            print(f"  {key}: {value}")

        print("\nTransaction:")
        print(f"  {tx_hash}")

        print("\nExplorer:")
        print(
            "  https://amoy.polygonscan.com/tx/"
            f"{tx_hash}"
        )

    else:

        print("                    ❌ VERIFICATION FAILED")
        print("=" * 70)

        print("\n⚠ Blockchain fingerprint does not")
        print("  match the recalculated local fingerprint.")

        print("\nThe record cannot be verified against")
        print("the supplied Polygon Amoy transaction.")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()