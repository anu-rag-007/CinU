from app.blockchain.fingerprint import create_fingerprint

def create_content_record(best_match: dict) -> dict:
    return {
        "platform": best_match.get("source"),
        "title": best_match.get("title"),
        "match_type": best_match.get("type"),
        "content_hash": best_match.get("content_hash"),
    }


def fingerprint_match(best_match: dict):

    record = create_content_record(best_match)

    fingerprint = create_fingerprint(record)

    return record, fingerprint