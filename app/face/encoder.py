import numpy as np
import cv2
from pathlib import Path
from insightface.app import FaceAnalysis


class FaceEncoder:
    def __init__(self):
        self.model = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )

        self.model.prepare(
            ctx_id=0,
            det_size=(640, 640)
        )

    def load_image(self, image_path: str) -> np.ndarray:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )
        
        image = cv2.imread(str(path))

        if image is None:
            raise ValueError(
                f"Could not read image: {image_path}"
            )
        return image

    def detect_faces(self, image: np.ndarray):
        faces = self.model.get(image)
        return faces

    def encode(self, image_path: str):
        image = self.load_image(image_path)
        faces = self.detect_faces(image)

        if len(faces) == 0:
            raise ValueError(
                "No face detected in the image."
            )

        results = []
        for index, face in enumerate(faces):
            embedding = face.embedding

            results.append(
                {
                    "face_index": index,
                    "embedding": embedding,
                    "bbox": face.bbox.tolist(),
                    "det_score": float(face.det_score),
                }
            )
        return results