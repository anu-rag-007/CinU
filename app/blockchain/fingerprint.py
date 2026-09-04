import hashlib
import json

def create_fingerprint(record: dict) -> str:
    canonical_data = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    fingerprint = hashlib.sha256(
        canonical_data.encode("utf-8")
    ).hexdigest()
    return fingerprint