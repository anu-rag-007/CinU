from pathlib import Path
from app.search.serpapi_client import SerpApiClient
from app.search.matcher import find_best_social_match
from app.blockchain.record import fingerprint_match
from app.blockchain.client import BlockchainClient

def main():
    project_root = Path(__file__).resolve().parent.parent
    image_path = project_root / "input" / "test.jpg"

    if not image_path.exists():
        raise FileNotFoundError(
            f"Test image not found: {image_path}"
        )

    print("=" * 60)
    print("CinU — WEB SEARCH")
    print("=" * 60)

    client = SerpApiClient()

    # --------------------------------------------------
    # Upload image
    # --------------------------------------------------

    print("\n[1/3] Uploading image...")

    upload_result = client.upload_image(
        str(image_path)
    )

    image_id = upload_result.get("image_id")

    if not image_id:
        raise RuntimeError(
            f"No image_id returned: {upload_result}"
        )

    print("      ✓ Image uploaded")
    print(f"      Image ID: {image_id}")

    # --------------------------------------------------
    # Google Lens
    # --------------------------------------------------

    print("\n[2/3] Searching with Google Lens...")

    exact_results = client.google_lens_search(
    image_id,
    "exact_matches"
    )

    visual_results = client.google_lens_search(
        image_id,
        "visual_matches"
    )

    lens_results = {
        "exact_matches": exact_results.get(
            "exact_matches",
            []
        ),
        "visual_matches": visual_results.get(
            "visual_matches",
            []
        ),
    }

    print("      ✓ Exact-match search completed")
    print("      ✓ Visual-match search completed")
    print("      ✓ Search completed")

    # --------------------------------------------------
    # Parse results
    # --------------------------------------------------
    
    best_match, all_results = find_best_social_match(lens_results)

    if not best_match:
        print("   \n❌ NO SOCIAL-MEDIA MATCH FOUND")
        print("     \nThe image may exist on the web, "
        "but no supported social-media match "
        "was discovered.")
        return
    
    print("\n" + "=" * 60)
    print("             CONTENT FINGERPRINT")
    print("=" * 60)
    
    record, fingerprint = fingerprint_match(best_match)
    print("\nCanonical record:")
    print(record)
    
    print("\nSHA-256 fingerprint:")
    print(f"  {fingerprint}")
    
    print("\n✓ Content fingerprint generated")
    
    
    print("\n" + "=" * 60)
    print("             BLOCKCHAIN RECORD")
    print("=" * 60)
    
    blockchain = BlockchainClient()
    
    print(f"\nWallet:")
    print(f"  {blockchain.address}")
    
    print(f"\nBalance:")
    print(f"  {blockchain.get_balance()} POL")
    
    print("\nRecording fingerprint on Polygon Amoy...")
    
    tx_hash = blockchain.store_hash(fingerprint)
    
    print("\n✓ Transaction submitted!")
    print(f"  TX Hash: {tx_hash}")
    
    print("\nWaiting for confirmation...")
    
    receipt = blockchain.web3.eth.wait_for_transaction_receipt(
        tx_hash,timeout=120,)
    
    if receipt.status == 1:
        print("\n✓ Blockchain transaction confirmed!")
        print(f"  Block: {receipt.blockNumber}")
        print(f"  TX Hash: {tx_hash}")
        print(f"  Explorer: https://amoy.polygonscan.com/tx/{tx_hash}")
    else:
        print("\n❌ Blockchain transaction failed.")  
        print("\n" + "=" * 60)
        print("SOCIAL MEDIA SEARCH")
        print("=" * 60)
        print(f"\n ✓ {len(all_results)} social-media " f"result(s) discovered")
    
    print("\n" + "=" * 60)
    print("CONTENT FINGERPRINT")
    print("=" * 60)
    record, fingerprint = fingerprint_match(best_match)
    print("\nCanonical record:")
    print(record)
    print("\nSHA-256 fingerprint:")
    print(f"  {fingerprint}")
    print("\n✓ Content fingerprint generated")
    print("\n" + "=" * 60)
    print("             SOCIAL MATCH FOUND")
    print("=" * 60)
    print(f"\nPlatform:")
    print(f"  📱 {best_match['source']}")
    print(f"\nTitle:")
    print(f"  {best_match['title']}")
    print(f"\nMatch type:")
    print(f"  {best_match['type']}")
    print(f"\nURL:")
    print(f"  {best_match['url']}")


    print("\n" + "-" * 60)
    print("OTHER SOCIAL-MEDIA MATCHES")
    print("-" * 60)

    for index, result in enumerate(
        all_results[:10],
        start=1
    ):

        print(
            f"\n{index}. "
            f"📱 [{result['source']}] "
            f"{result['title']}"
        )

        print(
            f"   Type: {result['type']}"
        )

        print(
            f"   URL: {result['url']}"
        )

    print("\n" + "=" * 60)
    print("✓ SOCIAL SEARCH SUCCESS")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()

    except FileNotFoundError as error:
        print(f"\n❌ ERROR: {error}")

    except RuntimeError as error:
        print(f"\n❌ ERROR: {error}")

    except Exception as error:
        print(
            f"\n❌ UNEXPECTED ERROR: {error}"
        )