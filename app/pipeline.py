from pathlib import Path
from app.face.encoder import FaceEncoder
from app.face.registry import load_registry
from app.face.matcher import find_best_match
from app.search.serpapi_client import SerpApiClient
from app.search.matcher import find_best_social_match
from app.blockchain.content_hash import sha256_file
from app.blockchain.record import fingerprint_match
from app.blockchain.client import BlockchainClient

def download_thumbnail(url, output_path):

    import requests

    if not url:
        raise ValueError(
            "No thumbnail URL returned."
        )

    response = requests.get(
        url,
        timeout=60
    )

    if not response.ok:
        raise RuntimeError(
            f"Thumbnail download failed "
            f"({response.status_code})"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_bytes(
        response.content
    )


def run_pipeline():

    project_root = (
        Path(__file__).resolve().parent.parent
    )

    input_image = (
        project_root
        / "input"
        / "test.jpg"
    )

    registry_path = (
        project_root
        / "output"
        / "face_registry.json"
    )

    discovered_path = (
        project_root
        / "output"
        / "discovered_content.jpg"
    )

    print("\n" + "=" * 70)
    print("                         CIN-U")
    print("                 END-TO-END PIPELINE")
    print("=" * 70)

    # ==================================================
    # 1. AUTHORIZED FACE REGISTRY
    # ==================================================

    print(
        "\n[1/7] Loading authorized face registry..."
    )

    registry = load_registry(
        str(registry_path)
    )

    print(
        f"✓ Loaded {len(registry)} authorized profiles"
    )

    # ==================================================
    # 2. FACE MATCH
    # ==================================================

    print(
        "\n[2/7] Scanning input image..."
    )

    encoder = FaceEncoder()

    faces = encoder.encode(
        str(input_image)
    )

    if len(faces) > 1:

        print(
            f"⚠ {len(faces)} faces detected. "
            "Using the first face."
        )

    query_embedding = (
        faces[0]["embedding"]
    )

    best_match, similarity = find_best_match(
        query_embedding,
        registry
    )

    if best_match is None:

        print(
            "\n❌ No authorized identity matched."
        )

        print(
            f"Best similarity: "
            f"{similarity:.4f}"
        )

        return

    profile_id = (
        best_match["profile_id"]
    )

    print(
        "\n✓ Authorized identity matched"
    )

    print(
        f"  Profile: {profile_id}"
    )

    print(
        f"  Name: "
        f"{best_match['display_name']}"
    )

    print(
        f"  Similarity: "
        f"{similarity:.4f}"
    )

    # ==================================================
    # 3. GOOGLE LENS
    # ==================================================

    print(
        "\n[3/7] Searching public web content..."
    )

    profile_image = (
        project_root
        / "data"
        / profile_id
        / "face.jpg"
    )

    serpapi = SerpApiClient()

    upload_result = serpapi.upload_image(
        str(profile_image)
    )

    image_id = upload_result["image_id"]

    print(
        "✓ Image uploaded to Google Lens"
    )

    exact_results = {}
    visual_results = {}

    try:

        exact_results = (
            serpapi.google_lens_search(
                image_id,
                search_type="exact_matches"
            )
        )

        print(
            "✓ Exact-match search completed"
        )

    except RuntimeError as error:

        print(
            f"⚠ Exact search unavailable: "
            f"{error}"
        )

    try:

        visual_results = (
            serpapi.google_lens_search(
                image_id,
                search_type="visual_matches"
            )
        )

        print(
            "✓ Visual-match search completed"
        )

    except RuntimeError as error:

        print(
            f"⚠ Visual search unavailable: "
            f"{error}"
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

    best_social, social_results = (
        find_best_social_match(
            lens_results
        )
    )

    if best_social is None:

        print(
            "\n❌ No social-media content found."
        )

        return

    # ==================================================
    # 4. DOWNLOAD CONTENT ARTIFACT
    # ==================================================

    print(
        "\n[4/7] Preparing discovered content..."
    )

    print(
        f"  Platform: "
        f"{best_social['source']}"
    )

    print(
        f"  Title: "
        f"{best_social['title']}"
    )

    print(
        f"  Match type: "
        f"{best_social['type']}"
    )

    thumbnail_url = (
        best_social.get("thumbnail")
    )

    if not thumbnail_url:

        print(
            "\n❌ No content thumbnail "
            "was returned."
        )

        return

    print(
        "\nDownloading content artifact..."
    )

    download_thumbnail(
        thumbnail_url,
        discovered_path
    )

    print(
        f"✓ Artifact saved:"
        f"\n  {discovered_path}"
    )

    # ==================================================
    # 5. CONTENT HASH
    # ==================================================

    print(
        "\n[5/7] Creating content fingerprint..."
    )

    content_hash = sha256_file(
        str(discovered_path)
    )

    best_social["content_hash"] = (
        content_hash
    )

    print(
        "\n✓ Content SHA-256:"
    )

    print(
        f"  {content_hash}"
    )

    record, fingerprint = (
        fingerprint_match(
            best_social
        )
    )

    print(
        "\n✓ Canonical record:"
    )

    for key, value in record.items():

        print(
            f"  {key}: {value}"
        )

    print(
        "\n✓ Record SHA-256:"
    )

    print(
        f"  {fingerprint}"
    )

    # ==================================================
    # 6. POLYGON
    # ==================================================

    print(
        "\n[6/7] Recording fingerprint "
        "on Polygon Amoy..."
    )

    blockchain = BlockchainClient()

    print(
        f"  Wallet: "
        f"{blockchain.address}"
    )

    print(
        f"  Balance: "
        f"{blockchain.get_balance()} POL"
    )

    tx_hash = blockchain.store_hash(
        fingerprint
    )

    print(
        "\n✓ Transaction submitted"
    )

    print(
        f"  TX Hash: {tx_hash}"
    )

    print(
        "\nWaiting for confirmation..."
    )

    receipt = (
        blockchain.web3.eth
        .wait_for_transaction_receipt(
            tx_hash,
            timeout=120
        )
    )

    if receipt.status != 1:

        print(
            "\n❌ Blockchain transaction failed."
        )

        return

    print(
        "\n✓ Blockchain transaction confirmed"
    )

    print(
        f"  Block: "
        f"{receipt.blockNumber}"
    )

    explorer_url = (
        "https://amoy.polygonscan.com/tx/"
        f"{tx_hash}"
    )

    print(
        f"  Explorer: {explorer_url}"
    )

    # ==================================================
    # 7. SUCCESS
    # ==================================================

    print(
        "\n[7/7] CIN-U verification record"
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "                       SUCCESS"
    )

    print(
        "=" * 70
    )

    print(
        f"\nIdentity:      "
        f"{best_match['display_name']}"
    )

    print(
        f"Profile ID:    "
        f"{profile_id}"
    )

    print(
        f"Similarity:    "
        f"{similarity:.4f}"
    )

    print(
        f"Platform:      "
        f"{best_social['source']}"
    )

    print(
        f"Content hash:  "
        f"{content_hash}"
    )

    print(
        f"Fingerprint:   "
        f"{fingerprint}"
    )

    print(
        f"TX Hash:       "
        f"{tx_hash}"
    )

    print(
        f"Explorer:      "
        f"{explorer_url}"
    )
    
    # ==================================================
    # SAVE VERIFICATION RECORD
    # ==================================================

    from app.blockchain.storage import save_record

    verification_record_path = (
        project_root
        / "output"
        / "records"
        / f"{tx_hash}.json"
    )

    save_record(
        record=record,
        fingerprint=fingerprint,
        tx_hash=tx_hash,
        output_path=str(
            verification_record_path
        )
    )

    print(
        "\n✓ Verification record saved:"
    )

    print(
        f"  {verification_record_path}"
    )

    print(
        "\n✓ CIN-U pipeline completed successfully."
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    run_pipeline()