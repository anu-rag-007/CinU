from pathlib import Path
from app.face.registry import build_registry, save_registry

def main():

    project_root = Path(__file__).resolve().parent.parent
    profiles_dir = project_root / "data"

    output_path = (
        project_root
        / "output"
        / "face_registry.json"
    )

    print("\n" + "=" * 60)
    print("             BUILDING FACE REGISTRY")
    print("=" * 60)

    registry = build_registry(
        str(profiles_dir)
    )

    if not registry:
        print("\n❌ No valid faces found.")
        return

    save_registry(
        registry,
        str(output_path)
    )

    print("\n" + "=" * 60)
    print("             REGISTRY COMPLETE")
    print("=" * 60)

    print(
        f"\n✓ Registered profiles: "
        f"{len(registry)}"
    )

    for profile in registry:
        print(
            f"  • {profile['profile_id']}"
        )


if __name__ == "__main__":
    main()