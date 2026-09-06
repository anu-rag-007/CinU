import json
import shutil
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    input_path = project_root / "input" / "test.jpg"

    print()
    print("=" * 60)
    print("CinU INPUT IMAGE SELECTOR")
    print("=" * 60)

    profiles = []
    for profile_dir in sorted(data_dir.iterdir()):
        if not profile_dir.is_dir():
            continue
        profile_path = profile_dir / "profile.json"
        image_path = profile_dir / "face.jpg"

        if not profile_path.exists():
            continue

        if not image_path.exists():
            continue

        try:
            with open(profile_path,"r",encoding="utf-8") as file:
                profile = json.load(file)

            profiles.append({
                "directory": profile_dir,
                "image": image_path,
                "profile_id": profile["profile_id"],
                "display_name": profile["display_name"],
            })

        except Exception as error:
            print(f" Could not read {profile_dir.name}: {error}")

    if not profiles:
        print()
        print(" No demo profiles found.")
        return

    print()
    print("Available demo identities:")
    print()
    for i, profile in enumerate(profiles,start=1):
        print(f"[{i}] "
            f"{profile['display_name']} "
            f"({profile['profile_id']})"
        )

    while True:
        choice = input("\nSelect demo image number: ").strip()

        try:
            selected_index = int(choice)

            if (1 <= selected_index <= len(profiles)):
                break

            print(f"Please enter a number between 1 and {len(profiles)}.")

        except ValueError:
            print("Please enter a valid number.")

    selected = profiles[selected_index - 1]

    input_path.parent.mkdir(parents=True,exist_ok=True)

    try:
        shutil.copy2(
            selected["image"],
            input_path
        )

    except Exception as error:
        print()
        print(f" Could not copy image: {error}")
        return

    print()
    print("=" * 60)
    print("INPUT IMAGE READY")
    print("=" * 60)
    print()
    print(f"Selected: {selected['display_name']}")
    print(f"Profile:  {selected['profile_id']}")

    print()
    print(f"Input image:")
    print(f" {input_path}")
    print()
    print(" Demo image copied to input/test.jpg")
    print()
    print("You can now run:")
    print(" python -m app.pipeline")
    print()

if __name__ == "__main__":
    main()