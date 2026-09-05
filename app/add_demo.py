import json
import shutil
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    print()
    print("=" * 60)
    print(" CIN-U ADD AUTHORIZED IDENTITY")
    print("=" * 60)

    profile_id = input("\nProfile ID (example: demo_04): ").strip()

    if not profile_id:
        print("\n Profile ID cannot be empty.")
        return

    profile_dir = data_dir / profile_id
    if profile_dir.exists():
        print()
        print(f" Profile '{profile_id}' already exists.")
        return

    display_name = input("Display name: ").strip()
    if not display_name:
        print("\n Display name cannot be empty.")
        return

    search_query = input("Search query: ").strip()

    if not search_query:
        search_query = display_name

    image_input = input("\nPath to face image: ").strip().strip('"')

    image_path = Path(image_input)

    if not image_path.exists():
        print()
        print(f" Image not found:\n{image_path}")
        return

    profile_dir.mkdir(parents=True,exist_ok=False)
    destination_image = (
        profile_dir / "face.jpg"
    )

    try:
        shutil.copy2(image_path,destination_image)

    except Exception as error:
        print()
        print(f" Could not copy image: {error}")

        shutil.rmtree(profile_dir,ignore_errors=True)
        return

    profile = {
        "profile_id": profile_id,
        "display_name": display_name,
        "search_query": search_query,
    }

    profile_path = (profile_dir / "profile.json")

    try:
        with open(
            profile_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                profile,
                file,
                indent=2,
                ensure_ascii=False
            )

    except Exception as error:
        print()
        print(f" Could not create profile: {error}")

        shutil.rmtree(profile_dir,ignore_errors=True)
        return

    print()
    print("=" * 60)
    print("IDENTITY ADDED SUCCESSFULLY")
    print("=" * 60)

    print()
    print(f"Profile ID:   {profile_id}")
    print(f"Name:         {display_name}")
    print(f"Search query: {search_query}")
    
    print()
    print("Created:")
    print(f"  {profile_dir}")
    print(f"  ├── face.jpg")
    print(f"  └── profile.json")

    print()
    print("CinU will automatically include this identity the next time the pipeline runs.")
    print()

if __name__ == "__main__":
    main()