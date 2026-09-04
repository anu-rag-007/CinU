from app.blockchain.fingerprint import create_fingerprint

def verify_record(record: dict, stored_fingerprint: str) -> bool:
    calculated_fingerprint = create_fingerprint(record)

    return calculated_fingerprint.lower() == stored_fingerprint.lower()