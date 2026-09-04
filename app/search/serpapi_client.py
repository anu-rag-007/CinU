import os
import requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

class SerpApiClient:
    IMAGE_API_URL = "https://serpapi.com/image"
    SEARCH_API_URL = "https://serpapi.com/search"

    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")

        if not self.api_key:
            raise RuntimeError(
                "SERPAPI_KEY is missing from .env"
            )

    def upload_image(self, image_path: str):
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        print(f"Uploading: {path}")

        with open(path, "rb") as image_file:
            files = {
                "image": (
                    path.name,
                    image_file,
                    "image/jpeg",
                )
            }

            data = {
                "api_key": self.api_key,
            }

            response = requests.post(
                self.IMAGE_API_URL,
                files=files,
                data=data,
                timeout=60,
            )

        if not response.ok:
            raise RuntimeError(
                f"SerpApi image upload failed"
                f"({response.status_code}): "
                f"{response.text}"
            )

        result = response.json()

        if "error" in result:
            raise RuntimeError(
                f"SerpApi error: {result['error']}"
            )

        if "image_id" not in result:
            raise RuntimeError(
                f"No image_id returned by SerpApi: {result}"
            )
        return result

    def google_lens_search(
        self,
        image_id: str,
        search_type: str = "exact_matches",
    ):
        params = {
            "engine": "google_lens",
            "image_id": image_id,
            "type": search_type,
            "api_key": self.api_key,
        }

        response = requests.get(
            self.SEARCH_API_URL,
            params=params,
            timeout=120,
        )

        if not response.ok:
            raise RuntimeError(
                f"Google Lens search failed "
                f"({response.status_code}): "
                f"{response.text}"
            )

        result = response.json()

        if "error" in result:
            raise RuntimeError(
                f"Google Lens error: {result['error']}"
            )
        return result