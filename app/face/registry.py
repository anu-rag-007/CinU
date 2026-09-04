import json
from pathlib import Path

import numpy as np

from app.face.encoder import FaceEncoder


def load_profile(profile_path: Path):
    with open(profile_path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_registry(profiles_dir: str):
    profiles_path = Path(profiles_dir)

    if not profiles_path.exists():
        raise FileNotFoundError(
            f"Profiles directory not found: {profiles_dir}"
        )

    encoder = FaceEncoder()
    registry = []

    for profile_dir in sorted(profiles_path.iterdir()):

        if not profile_dir.is_dir():
            continue

        image_path = profile_dir / "face.jpg"
        profile_path = profile_dir / "profile.json"

        if not image_path.exists():
            print(
                f"⚠ Skipping {profile_dir.name}: "
                "face.jpg not found"
            )
            continue

        if not profile_path.exists():
            print(
                f"⚠ Skipping {profile_dir.name}: "
                "profile.json not found"
            )
            continue

        print(f"\nProcessing {profile_dir.name}...")

        try:
            profile = load_profile(profile_path)
            faces = encoder.encode(str(image_path))

        except Exception as error:
            print(f"❌ Failed: {error}")
            continue

        if not faces:
            print("❌ No face detected")
            continue

        if len(faces) > 1:
            print(
                f"⚠ Multiple faces found in "
                f"{profile_dir.name}. Using the first face."
            )

        embedding = faces[0]["embedding"]

        registry.append(
            {
                "profile_id": profile["profile_id"],
                "display_name": profile["display_name"],
                "search_query": profile["search_query"],
                "embedding": embedding.tolist(),
            }
        )

        print("✓ Face encoded")
        print(f"  Name: {profile['display_name']}")
        print(f"  Search: {profile['search_query']}")

    return registry


def save_registry(registry, output_path: str):
    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            registry,
            file,
            indent=2
        )

    print(f"\n✓ Registry saved to: {path}")


def load_registry(registry_path: str):
    path = Path(registry_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Registry not found: {registry_path}"
        )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def registry_embeddings(registry):
    return [
        np.asarray(
            item["embedding"],
            dtype=np.float32
        )
        for item in registry
    ]