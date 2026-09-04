from pathlib import Path
import requests
from app.face.encoder import FaceEncoder
from app.face.registry import load_registry
from app.face.matcher import find_best_match
from app.search.serpapi_client import SerpApiClient
from app.search.matcher import find_best_social_match
from app.blockchain.content_hash import sha256_file


def download_thumbnail(url, output_path):

    if not url:
        raise ValueError(
            "No thumbnail URL was returned by Google Lens."
        )

    print("\nDownloading discovered content thumbnail...")

    response = requests.get(
        url,
        timeout=60
    )

    if not response.ok:
        raise RuntimeError(
            f"Thumbnail download failed "
            f"({response.status_code}): "
            f"{response.text}"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_bytes(
        response.content
    )

    print(
        f"✓ Thumbnail saved to: {output_path}"
    )

    return output_path


def main():

    project_root = (
        Path(__file__).resolve().parents[2]
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

    print("\n" + "=" * 60)
    print("              CIN-U PROFILE SEARCH")
    print("=" * 60)

    # --------------------------------------------------
    # 1. LOAD REGISTRY
    # --------------------------------------------------

    print("\n[1] Loading authorized registry...")

    registry = load_registry(
        str(registry_path)
    )

    print(
        f"✓ Loaded {len(registry)} profiles"
    )

    # --------------------------------------------------
    # 2. FACE MATCH
    # --------------------------------------------------

    print("\n[2] Matching input face...")

    encoder = FaceEncoder()

    faces = encoder.encode(
        str(input_image)
    )

    query_embedding = faces[0]["embedding"]

    best_match, similarity = find_best_match(
        query_embedding,
        registry
    )

    if best_match is None:

        print(
            "\n❌ No authorized profile matched."
        )

        print(
            f"Best similarity: {similarity:.4f}"
        )

        return

    profile_id = best_match["profile_id"]

    print("\n✓ Authorized profile matched")

    print(
        f"  Profile ID: {profile_id}"
    )

    print(
        f"  Name: {best_match['display_name']}"
    )

    print(
        f"  Similarity: {similarity:.4f}"
    )

    # --------------------------------------------------
    # 3. GOOGLE LENS
    # --------------------------------------------------

    print("\n[3] Searching public web content...")

    profile_image = (
        project_root
        / "data"
        / profile_id
        / "face.jpg"
    )

    serpapi = SerpApiClient()

    print(
        f"  Using: {profile_image}"
    )

    upload_result = serpapi.upload_image(
        str(profile_image)
    )

    image_id = upload_result["image_id"]

    print(
        f"✓ Image uploaded"
    )

    print(
        f"  Image ID: {image_id}"
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
            f"⚠ No exact matches: {error}"
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
            f"⚠ No visual matches: {error}"
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

    # --------------------------------------------------
    # 4. FIND SOCIAL RESULT
    # --------------------------------------------------

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

    print("\n" + "=" * 60)
    print("              DISCOVERED CONTENT")
    print("=" * 60)

    print(
        "\n✓ Best social result found"
    )

    print(
        f"\nPlatform:\n  "
        f"{best_social['source']}"
    )

    print(
        f"\nTitle:\n  "
        f"{best_social['title']}"
    )

    print(
        f"\nMatch type:\n  "
        f"{best_social['type']}"
    )

    print(
        f"\nURL:\n  "
        f"{best_social.get('url')}"
    )

    print(
        f"\nGoogle Lens redirect:\n  "
        f"{best_social.get('redirect_url')}"
    )

    # --------------------------------------------------
    # 5. DOWNLOAD THUMBNAIL
    # --------------------------------------------------

    thumbnail_url = best_social.get(
        "thumbnail"
    )

    if not thumbnail_url:

        print(
            "\n❌ No thumbnail returned."
        )

        return

    thumbnail_path = (
        project_root
        / "output"
        / "discovered_content.jpg"
    )

    download_thumbnail(
        thumbnail_url,
        thumbnail_path
    )

    # --------------------------------------------------
    # 6. HASH CONTENT
    # --------------------------------------------------

    print(
        "\nCreating content fingerprint..."
    )

    content_hash = sha256_file(
        str(thumbnail_path)
    )

    best_social["content_hash"] = (
        content_hash
    )

    best_social["thumbnail_path"] = (
        str(thumbnail_path)
    )

    print(
        "\n✓ Content SHA-256:"
    )

    print(
        f"  {content_hash}"
    )

    # --------------------------------------------------
    # 7. FINAL RESULT
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("                     SUCCESS")
    print("=" * 60)

    print(
        f"\nProfile:       "
        f"{best_match['display_name']}"
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
        f"Title:         "
        f"{best_social['title']}"
    )

    print(
        f"Content hash:  "
        f"{content_hash}"
    )

    print(
        f"Artifact:      "
        f"{thumbnail_path}"
    )

    print(
        "\n✓ Content artifact successfully "
        "prepared for blockchain recording."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()