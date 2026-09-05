import json
import hashlib
from pathlib import Path

import requests

from app.face.encoder import FaceEncoder
from app.face.registry import build_registry, save_registry
from app.face.matcher import find_best_match

from app.search.serpapi_client import SerpApiClient
from app.search.matcher import find_best_social_match

from app.blockchain.content_hash import sha256_file
from app.blockchain.record import fingerprint_match
from app.blockchain.client import BlockchainClient
from app.blockchain.fingerprint import create_fingerprint


# ============================================================
# DOWNLOAD THUMBNAIL
# ============================================================

def download_thumbnail(url, output_path):
    """
    Download the thumbnail/image associated with the
    selected social-media search result.
    """

    if not url:
        raise ValueError(
            "No thumbnail URL returned."
        )

    response = requests.get(
        url,
        timeout=60,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120 Safari/537.36"
            )
        }
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


# ============================================================
# SAVE ALL SOCIAL RESULTS
# ============================================================

def save_social_results(results, output_path):
    """
    Save every discovered social-media result
    to a JSON file.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# AUTOMATIC VERIFICATION
# ============================================================

def automatic_verify(
    blockchain,
    tx_hash,
    record_path,
    discovered_path
):
    """
    Automatically verify:

    1. Discovered content SHA-256
    2. Local record fingerprint
    3. Local fingerprint against Polygon Amoy
    4. Blockchain transaction integrity
    """

    print()
    print("=" * 70)
    print("                    AUTOMATIC VERIFICATION")
    print("=" * 70)

    try:

        # ----------------------------------------------------
        # Load saved record
        # ----------------------------------------------------

        with open(
            record_path,
            "r",
            encoding="utf-8"
        ) as f:

            saved = json.load(f)

        record = saved["record"]

        saved_fingerprint = (
            saved["fingerprint"]
        )

        # ----------------------------------------------------
        # 1. Verify discovered content
        # ----------------------------------------------------

        current_content_hash = (
            sha256_file(
                discovered_path
            )
        )

        if (
            current_content_hash
            == record["content_hash"]
        ):

            print(
                "✓ Content file matches "
                "recorded SHA-256"
            )

            content_ok = True

        else:

            print(
                "✗ Content file does NOT "
                "match recorded SHA-256"
            )

            content_ok = False

        # ----------------------------------------------------
        # 2. Verify local record fingerprint
        # ----------------------------------------------------

        local_fingerprint = (
            create_fingerprint(record)
        )

        if (
            local_fingerprint
            == saved_fingerprint
        ):

            print(
                "✓ Local record fingerprint is valid"
            )

            local_ok = True

        else:

            print(
                "✗ Local record fingerprint "
                "is invalid"
            )

            local_ok = False

        # ----------------------------------------------------
        # 3. Verify fingerprint on Polygon
        # ----------------------------------------------------

        polygon_ok = False

        try:

            on_chain_data = blockchain.get_transaction_data(tx_hash)

            if isinstance(
                on_chain_data,
                str
            ):

                if on_chain_data.startswith(
                    "0x"
                ):

                    on_chain_data = (
                        on_chain_data[2:]
                    )

                on_chain_data = (
                    on_chain_data.lower()
                )

            expected_fingerprint = (
                saved_fingerprint.lower()
            )

            if (
                on_chain_data
                == expected_fingerprint
            ):

                print(
                    "✓ Local fingerprint "
                    "matches Polygon Amoy"
                )

                polygon_ok = True

            else:

                print(
                    "✗ Local fingerprint does "
                    "NOT match Polygon Amoy"
                )

        except Exception as error:

            print(
                "✗ Could not verify Polygon "
                f"transaction: {error}"
            )

        # ----------------------------------------------------
        # 4. Blockchain record
        # ----------------------------------------------------

        if polygon_ok:

            print(
                "✓ Blockchain record is intact"
            )

            blockchain_ok = True

        else:

            print(
                "✗ Blockchain record "
                "verification failed"
            )

            blockchain_ok = False

        # ----------------------------------------------------
        # Final verification
        # ----------------------------------------------------

        verified = (
            content_ok
            and local_ok
            and polygon_ok
            and blockchain_ok
        )

        print()
        print("TX Hash:")
        print(tx_hash)

        print("=" * 70)

        if verified:

            print()
            print(
                "Verification:  ✅ VERIFIED"
            )

        else:

            print()
            print(
                "Verification:  ❌ FAILED"
            )

        return verified

    except Exception as error:

        print()
        print(
            f"✗ Automatic verification failed: "
            f"{error}"
        )

        return False


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline():

    # ========================================================
    # PROJECT PATHS
    # ========================================================

    project_root = (
        Path(__file__).resolve().parent.parent
    )

    input_image = (
        project_root
        / "input"
        / "test.jpg"
    )
    
    profiles_dir = (
        project_root
        / "data"
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

    social_results_path = (
        project_root
        / "output"
        / "social_results.json"
    )

    records_dir = (
        project_root
        / "output"
        / "records"
    )

    # ========================================================
    # HEADER
    # ========================================================

    print()
    print("=" * 70)
    print("                         CIN-U")
    print("                 END-TO-END PIPELINE")
    print("=" * 70)

    print()
    print("Input image:")
    print(f"  {input_image}")

    # ========================================================
    # CHECK INPUT
    # ========================================================

    if not input_image.exists():

        print()
        print(
            "✗ Input image does not exist:"
        )

        print(
            input_image
        )

        return

    # ========================================================
    # 1. AUTHORIZED FACE REGISTRY
    # ========================================================

    print("[1/7] Building authorized face registry...")

    try:

        print()
        print("Scanning authorized profiles...")

        registry = build_registry(
            str(profiles_dir)
        )

        if not registry:

            print()
            print("✗ No valid authorized profiles found.")

            return

        save_registry(
            registry,
            str(registry_path)
        )

        print()
        print(f"✓ Registry updated with "f"{len(registry)} authorized profiles")

    except Exception as error:

        print()
        print(f"✗ Could not build face registry: "f"{error}")

        return
    
    # ========================================================
    # 2. FACE DETECTION + MATCHING
    # ========================================================

    print()
    print(
        "[2/7] Scanning input image..."
    )

    try:

        encoder = FaceEncoder()

        # IMPORTANT:
        # Your FaceEncoder uses encode(),
        # NOT encode_image().

        faces = encoder.encode(
            str(input_image)
        )

        if not faces:

            print()
            print(
                "✗ No face detected."
            )

            return

        print(
            f"✓ Detected {len(faces)} face(s)"
        )

        if len(faces) > 1:

            print(
                f"⚠ {len(faces)} faces detected. "
                "Using the first face."
            )

        query_embedding = (
            faces[0]["embedding"]
        )

        best_match, similarity = (
            find_best_match(
                query_embedding,
                registry
            )
        )

        if best_match is None:

            print()
            print(
                "❌ No authorized identity matched."
            )

            print(
                f"Best similarity: "
                f"{similarity:.4f}"
            )

            return

        profile_id = (
            best_match["profile_id"]
        )

        print()
        print(
            "✓ Authorized identity matched"
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

    except Exception as error:

        print()
        print(
            f"✗ Face detection failed: "
            f"{error}"
        )

        return

    # ========================================================
    # 3. GOOGLE LENS / PUBLIC CONTENT SEARCH
    # ========================================================

    print()
    print(
        "[3/7] Searching public web content..."
    )

    try:

        profile_image = (
            project_root
            / "data"
            / profile_id
            / "face.jpg"
        )

        if not profile_image.exists():

            print()
            print(
                "✗ Profile image not found:"
            )

            print(
                profile_image
            )

            return

        serpapi = SerpApiClient()

        # ----------------------------------------------------
        # Upload image
        # ----------------------------------------------------

        print()
        print(
            "Uploading image to Google Lens..."
        )

        upload_result = (
            serpapi.upload_image(
                str(profile_image)
            )
        )

        image_id = (
            upload_result["image_id"]
        )

        print(
            "✓ Image uploaded to Google Lens"
        )

        # ----------------------------------------------------
        # Exact matches
        # ----------------------------------------------------

        exact_results = {}

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

        # ----------------------------------------------------
        # Visual matches
        # ----------------------------------------------------

        visual_results = {}

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

        # ----------------------------------------------------
        # Combine Lens results
        # ----------------------------------------------------

        lens_results = {

            "exact_matches":
                exact_results.get(
                    "exact_matches",
                    []
                ),

            "visual_matches":
                visual_results.get(
                    "visual_matches",
                    []
                ),
        }

        # ----------------------------------------------------
        # Find social-media results
        # ----------------------------------------------------

        best_social, social_results = (
            find_best_social_match(
                lens_results
            )
        )

        if not social_results:

            print()
            print(
                "⚠ No social-media results discovered."
            )

            return

        # ====================================================
        # SAVE ALL SOCIAL RESULTS
        # ====================================================

        save_social_results(
            social_results,
            social_results_path
        )

        # ====================================================
        # DISPLAY TOP 10 RESULTS
        # ====================================================

        print()
        print("=" * 70)
        print(
            "                 DISCOVERED SOCIAL CONTENT"
        )
        print("=" * 70)

        display_results = (
            social_results[:10]
        )

        for index, result in enumerate(
            display_results,
            start=1
        ):

            platform = result.get(
                "source",
                "Unknown"
            )

            title = result.get(
                "title",
                "Untitled"
            )

            match_type = result.get(
                "type",
                "unknown"
            )

            url = result.get(
                "url"
            )

            redirect_url = result.get(
                "redirect_url"
            )

            print()
            print(
                f"[{index}] {platform}"
            )

            print(
                f"    Title: {title}"
            )

            print(
                f"    Type:  {match_type}"
            )

            if url:

                print(
                    f"    URL:   {url}"
                )

            elif redirect_url:

                print(
                    f"    URL:   {redirect_url}"
                )

            else:

                print(
                    "    URL:   Not available"
                )

        # ----------------------------------------------------
        # Remaining results
        # ----------------------------------------------------

        remaining = (
            len(social_results)
            - len(display_results)
        )

        if remaining > 0:

            print()
            print(
                f"... and {remaining} more results."
            )

        print()
        print(
            f"Total discovered social results: "
            f"{len(social_results)}"
        )

        print()
        print(
            "Complete results saved to:"
        )

        print(
            f"  {social_results_path}"
        )

        # ====================================================
        # BEST SOCIAL RESULT
        # ====================================================

        if best_social is None:

            print()
            print(
                "⚠ No best social result available."
            )

            return

        print()
        print("-" * 70)
        print(
            "BEST SOCIAL RESULT"
        )
        print("-" * 70)

        print()

        print(
            f"Platform: "
            f"{best_social.get('source')}"
        )

        print(
            f"Title:    "
            f"{best_social.get('title')}"
        )

        print(
            f"Type:     "
            f"{best_social.get('type')}"
        )

        if best_social.get("url"):

            print(
                f"URL:      "
                f"{best_social.get('url')}"
            )

        elif best_social.get(
            "redirect_url"
        ):

            print(
                f"URL:      "
                f"{best_social.get('redirect_url')}"
            )

    except Exception as error:

        print()
        print(
            f"✗ Search failed: "
            f"{error}"
        )

        return

    # ========================================================
    # 4. DOWNLOAD DISCOVERED CONTENT
    # ========================================================

    print()
    print(
        "[4/7] Downloading discovered content..."
    )

    try:

        thumbnail_url = (
            best_social.get(
                "thumbnail"
            )
            or
            best_social.get(
                "thumbnail_url"
            )
        )

        if not thumbnail_url:

            print()
            print(
                "✗ No thumbnail available "
                "for the best result."
            )

            return

        download_thumbnail(
            thumbnail_url,
            discovered_path
        )

        print(
            "✓ Discovered content downloaded"
        )

        print(
            f"  Saved to: "
            f"{discovered_path}"
        )

    except Exception as error:

        print()
        print(
            f"✗ Content download failed: "
            f"{error}"
        )

        return

    # ========================================================
    # 5. CREATE CONTENT HASH + FINGERPRINT
    # ========================================================

    print()
    print(
    "[5/7] Creating content fingerprint..."
    )

    try:
        content_hash = (
        sha256_file(
            discovered_path
        )
    )

        print()
        print("SHA-256:")
        print(content_hash)

    
        best_social["content_hash"] = content_hash

    
        record, fingerprint = fingerprint_match(best_social)

        print()
        print("Record:")
        print(record)

        print()
        print("Fingerprint:")
        print(fingerprint)

    except Exception as error:

        print()
        print(f"❌ Fingerprint creation failed: {error}")

        return

        # ----------------------------------------------------
        # Blockchain record
        # ----------------------------------------------------

        record = {

            "platform":
                best_social.get(
                    "source"
                ),

            "title":
                best_social.get(
                    "title"
                ),

            "match_type":
                best_social.get(
                    "type"
                ),

            "content_hash":
                content_hash,
        }

        fingerprint = (
            fingerprint_match(
                record
            )
        )

        print()
        print(
            "Record fingerprint:"
        )

        print(
            fingerprint
        )

    except Exception as error:

        print()
        print(
            f"✗ Fingerprint creation failed: "
            f"{error}"
        )

        return

    # ========================================================
    # 6. POLYGON AMOY
    # ========================================================

    print()
    print("[6/7] Recording fingerprint on Polygon Amoy...")

    try:
        blockchain = BlockchainClient()

        print()
        print(f"Wallet: {blockchain.address}")
        print(f"Balance: {blockchain.get_balance()} POL")

        print()
        print()
        print("Sending fingerprint to Polygon Amoy...")

        print()
        print("DEBUG FINGERPRINT:")
        print(fingerprint)
        print(f"Length: {len(fingerprint)}")
        print(f"Hex characters only: "f"{all(c in '0123456789abcdefABCDEF' for c in fingerprint)}")

        tx_hash = blockchain.store_hash(fingerprint)

        print()
        print("✓ Transaction submitted")

        print()
        print("TX Hash:")
        print(tx_hash)

        print()
        print("Waiting for confirmation...")

        receipt = blockchain.web3.eth.wait_for_transaction_receipt(tx_hash,timeout=120)

        if receipt.status != 1:
            print()
            print("❌ Blockchain transaction failed.")
            return

        print()
        print("✓ Blockchain transaction confirmed")

        print()
        print(f"Block: {receipt.blockNumber}")

        explorer_url = ("https://amoy.polygonscan.com/tx/" + tx_hash)
        print()
        print("Explorer:")
        print(explorer_url)

    except Exception as error:
        print()
        print(f"✗ Blockchain transaction failed: {error}")
        return
    
    # ========================================================
    # SAVE VERIFICATION RECORD
    # ========================================================

    print()
    print(
        "Saving verification record..."
    )

    try:

        records_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        record_path = (
            records_dir
            / f"{tx_hash}.json"
        )

        saved_record = {

            "record":
                record,

            "fingerprint":
                fingerprint,

            "tx_hash":
                tx_hash,
        }

        with open(
            record_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                saved_record,
                f,
                indent=2,
                ensure_ascii=False
            )

        print()
        print(
            "✓ Verification record saved"
        )

        print(
            f"  {record_path}"
        )

    except Exception as error:

        print()
        print(
            f"✗ Could not save verification record: "
            f"{error}"
        )

        return

    # ========================================================
    # 7. AUTOMATIC VERIFICATION
    # ========================================================

    print()
    print(
        "[7/7] Automatically verifying..."
    )

    verified = automatic_verify(
        blockchain,
        tx_hash,
        record_path,
        discovered_path
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print(
        "                    CIN-U COMPLETE"
    )
    print("=" * 70)

    print()

    print(
        f"Identity:      "
        f"{best_match.get('display_name')}"
    )

    print(
        f"Profile ID:    "
        f"{best_match.get('profile_id')}"
    )

    print(
        f"Similarity:    "
        f"{similarity:.4f}"
    )

    print(
        f"Social results: "
        f"{len(social_results)}"
    )

    print(
        f"Best platform: "
        f"{best_social.get('source')}"
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

    print()

    print(
        f"Results JSON:   "
        f"{social_results_path}"
    )

    print()

    if verified:

        print(
            "Verification:  ✅ VERIFIED"
        )

    else:

        print(
            "Verification:  ❌ FAILED"
        )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_pipeline()