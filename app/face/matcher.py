import numpy as np

def cosine_similarity(a, b):
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)

    denominator = (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)


def find_best_match(query_embedding,registry,threshold=0.45):
    best_match = None
    best_score = -1.0

    for profile in registry:
        stored_embedding = np.asarray(
            profile["embedding"],
            dtype=np.float32
        )

        score = cosine_similarity(
            query_embedding,
            stored_embedding
        )

        if score > best_score:
            best_score = score
            best_match = profile

    if best_match is None:
        return None, 0.0

    if best_score < threshold:
        return None, best_score

    return best_match, best_score