from pathlib import Path
from app.face.encoder import FaceEncoder
from app.face.registry import load_registry
from app.face.matcher import find_best_match
from app.face.profile import get_profile_by_id


def main():
    project_root = Path(__file__).resolve().parents[2]

    image_path = project_root / "input" / "test.jpg"
    registry_path = project_root / "output" / "face_registry.json"

    print("\n" + "=" * 60)
    print("                 CIN-U FACE MATCHING")
    print("=" * 60)

    # ---------------------------------------------------------
    # Load authorized registry
    # ---------------------------------------------------------

    registry = load_registry(str(registry_path))

    print(
        f"\n✓ Loaded {len(registry)} authorized profiles"
    )

    # ---------------------------------------------------------
    # Encode input image
    # ---------------------------------------------------------

    encoder = FaceEncoder()

    print("\nScanning input image...")

    faces = encoder.encode(str(image_path))

    if len(faces) > 1:
        print(
            f"⚠ Multiple faces detected. "
            f"Using the first face."
        )

    query_embedding = faces[0]["embedding"]

    print("✓ Input face encoded")

    # ---------------------------------------------------------
    # Match against registry
    # ---------------------------------------------------------

    print("\nComparing against authorized profiles...")

    best_match, score = find_best_match(
        query_embedding,
        registry
    )

    print("\n" + "-" * 60)

    if best_match is None:
        print("❌ NO AUTHORIZED MATCH")
        print(f"Best similarity: {score:.4f}")
        print("-" * 60)
        return

    print("✓ AUTHORIZED MATCH FOUND")
    print(f"Profile:     {best_match['profile_id']}")
    print(f"Name:        {best_match['display_name']}")
    print(f"Similarity:  {score:.4f}")

    print("-" * 60)

    # ---------------------------------------------------------
    # Retrieve profile
    # ---------------------------------------------------------

    profile = get_profile_by_id(
        registry,
        best_match["profile_id"]
    )

    if profile is None:
        print("\n❌ Profile information not found.")
        return

    print("\n" + "=" * 60)
    print("              AUTHORIZED PROFILE")
    print("=" * 60)

    print(f"\nProfile ID:")
    print(f"  {profile['profile_id']}")

    print(f"\nDisplay Name:")
    print(f"  {profile['display_name']}")

    print(f"\nSearch Query:")
    print(f"  {profile['search_query']}")

    print("\n✓ Profile successfully resolved")


if __name__ == "__main__":
    main()