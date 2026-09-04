import numpy as np
from pathlib import Path 
import argparse
from app.face.encoder import FaceEncoder

def main():
    parser = argparse.ArgumentParser(
        description="CinU : Face ID & Blockchain Verification"
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Path to the input Image"
    )
    args = parser.parse_args()
    print("=" * 50)
    print("CinU is working...😒")
    print("=" * 50)

    print("\n[1/3] Loading face recognition model...😴")

    encoder = FaceEncoder()

    print("Model loaded")

    print("\n[2/3] Detecting your Beautiful face...🥰")

    faces = encoder.encode(args.image)
    
    output_dir = Path("../output")
    output_dir.mkdir(exist_ok=True)
    
    for face in faces:
        embedding_path = (
            output_dir / f"face_{face['face_index']+1}_embedding.npy"
        )
        
    np.save(
        embedding_path,
        face['embedding'] 
    )
    print(
        f"Saved Embedding: {embedding_path}"
    )
    print(f"{len(faces)} face(s) detected")

    print("\n[3/3] Generating embeddings...🐣")

    for face in faces:
        embedding = face["embedding"]
        print(f"\nFace #{face['face_index'] + 1}")
        print(f"Detection confidence: {face['det_score']:.4f}")
        print(f"Bounding box: {face['bbox']}")
        print(f"Embedding dimensions: {embedding.shape}")
        print(f"First 5 values: "
            f"{embedding[:5]}"
        )

    print("\n" + "=" * 50)
    print("SUCCESS 🙌")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()

    except FileNotFoundError as error:
        print(f"\n❌ ERROR: {error}")

    except ValueError as error:
        print(f"\n❌ ERROR: {error}")

    except Exception as error:
        print(f"\n❌ UNEXPECTED ERROR: {error}")