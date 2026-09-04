import json
from pathlib import Path

def save_record(record: dict, fingerprint: str, tx_hash: str, output_path: str):
    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = {
        "record": record,
        "fingerprint": fingerprint,
        "tx_hash": tx_hash,
    }

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


def load_record(output_path: str):

    path = Path(output_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Verification record not found: {path}"
        )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)