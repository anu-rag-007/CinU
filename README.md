# CinU — Face ID + Blockchain Verification

CinU is a consent-based hackathon prototype for verifying whether public online content associated with an **authorized demo identity** can be cryptographically verified after discovery.

## Features

- Authorized face registry
- Face detection and embeddings with InsightFace
- Cosine-similarity face matching
- Google Lens public-content discovery through SerpApi
- Social-media result filtering
- SHA-256 content hashing
- Canonical cryptographic record fingerprinting
- Polygon Amoy blockchain recording
- Automatic local and on-chain verification
- Dynamic addition of new demo identities
- Interactive input-image selection

> **Important:** The blockchain proves the integrity of the recorded fingerprint, not the truth, ownership, or real-world identity of a person or social-media post.

---

## 1. End-to-End Architecture

```text
Authorized Identity
        ↓
Face Detection
        ↓
Face Embedding
        ↓
Authorized Identity Matching
        ↓
Google Lens / Public Content Search
        ↓
Social-Media Result Discovery
        ↓
Content Download
        ↓
SHA-256 Content Hash
        ↓
Cryptographic Record Fingerprint
        ↓
Polygon Amoy
        ↓
Automatic Verification
        ↓
VERIFIED
```

---

## 2. Project Structure

```text
CinU/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── pipeline.py
│   ├── add_demo.py
│   ├── select_input.py
│   ├── registry_test.py
│   ├── search_test.py
│   ├── verify.py
│   ├── verify_test.py
│   ├── blockchain_test.py
│   │
│   ├── face/
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   ├── encoder.py
│   │   ├── match_test.py
│   │   ├── matcher.py
│   │   ├── profile.py
│   │   └── registry.py
│   │
│   ├── hashing/
│   │   └── fingerprint.py
│   │
│   ├── search/
│   │   ├── __init__.py
│   │   ├── matcher.py
│   │   ├── profile_search_test.py
│   │   └── serpapi_client.py
│   │
│   └── blockchain/
│       ├── client.py
│       ├── content_hash.py
│       ├── contract.py
│       ├── fingerprint.py
│       ├── record.py
│       ├── storage.py
│       └── verify.py
│
├── contracts/
├── data/
│   ├── demo_01/
│   ├── demo_02/
│   ├── demo_03/
│   ├── demo_04/
│   └── demo_05/
├── input/
│   └── test.jpg
├── output/
│   ├── discovered_content.jpg
│   ├── face_registry.json
│   ├── face_1_embedding.npy
│   ├── social_results.json
│   └── records/
├── tests/
│   ├── test_hashing.py
│   └── test_verification.py
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 3. Authorized Face Registry

Each authorized demo identity is stored under `data/`:

```text
data/demo_01/
├── face.jpg
└── profile.json
```

Example `profile.json`:

```json
{
  "profile_id": "demo_01",
  "display_name": "Demo Person 01",
  "search_query": "Demo Person 01"
}
```

The registry scans the `data/` directory and generates embeddings using InsightFace.

The generated registry is saved to:

```text
output/face_registry.json
```

### Dynamic Registry

The pipeline now **rebuilds the registry every time it runs**.

Therefore, if a new profile is added:

```text
data/demo_06/
├── face.jpg
└── profile.json
```

the next pipeline run automatically discovers and encodes it.

There is no need to manually rebuild the registry first.

---

## 4. Adding a New Demo Identity

CinU includes an interactive identity creator:

```powershell
python -m app.add_demo
```

It asks for:

```text
Profile ID
Display name
Search query
Path to face image
```

It then creates:

```text
data/<profile_id>/
├── face.jpg
└── profile.json
```

This is useful for demonstrating that identities can be added dynamically.

---

## 5. Selecting the Input Image

CinU includes an interactive input selector:

```powershell
python -m app.select_input
```

It scans the available demo profiles and displays them:

```text
Available demo identities:

[1] Demo Person 01 (demo_01)
[2] Demo Person 02 (demo_02)
[3] Demo Person 03 (demo_03)
[4] Demo Person 04 (demo_04)
[5] Demo Person 05 (demo_05)

Select demo image number:
```

The selected profile's `face.jpg` is copied to:

```text
input/test.jpg
```

This allows different authorized demo identities to be tested without manually replacing files.

---

## 6. Face Detection and Matching

CinU uses:

- InsightFace
- `buffalo_l`
- ONNX Runtime
- OpenCV
- NumPy

The encoder detects faces and generates embeddings.

The matching stage compares the input embedding with the authorized registry using cosine similarity.

Example:

```text
✓ Authorized identity matched
  Profile: demo_01
  Name: Demo Person 01
  Similarity: 1.0000
```

The actual similarity depends on the input image.

---

## 7. Public Content Search

After an authorized identity is matched, CinU uses that authorized profile's image for public web-content discovery.

Google Lens is accessed through SerpApi.

The search process is:

1. Upload image
2. Run exact-match search
3. Run visual-match search
4. Combine results
5. Filter social-media results
6. Select the best result

The project recognizes social sources including:

- Instagram
- Facebook
- X/Twitter
- TikTok
- YouTube
- LinkedIn
- Reddit

All discovered social results are saved to:

```text
output/social_results.json
```

### Interpretation

Search results represent **public content related to the searched image/content**. They should not be described as definitive proof that a result belongs to the matched person's account.

---

## 8. Downloaded Content

The selected result's thumbnail/content is downloaded to:

```text
output/discovered_content.jpg
```

This local file is used for the cryptographic integrity checks.

---

## 9. SHA-256 Content Hash

CinU calculates a SHA-256 hash of the discovered content.

Example:

```text
SHA-256:
d4f604f68c9b5d78b18a36fa05e11559213932f36ee26fde8c41a32171621296
```

During verification, the file is hashed again and compared with the recorded hash.

Conceptually:

```text
Downloaded Content
       ↓
    SHA-256
       ↓
 Content Hash
```

---

## 10. Cryptographic Fingerprint

CinU creates a canonical record containing information about the discovered content.

The canonical record is deterministically serialized and hashed using SHA-256.

Example fingerprint:

```text
931f0c284bd0a482caddd9388ee8679af65a15e6ff1c2f1bf64af37d471356f1
```

The fingerprint provides a compact cryptographic representation of the recorded information.

---

## 11. Polygon Amoy

CinU records the fingerprint on the Polygon Amoy testnet.

The image itself is **not** stored on-chain.

The flow is:

```text
Content
   ↓
SHA-256
   ↓
Record
   ↓
Fingerprint
   ↓
Polygon Amoy transaction
```

After the transaction is confirmed, CinU displays the transaction hash and Polygon explorer URL.

Example:

```text
TX Hash:
a0f66d842642cedf39b9460ec7c4a423915acbef30375df73b3118f4cb4e44bc
```

---

## 12. Local Verification Record

After the blockchain transaction succeeds, CinU saves a verification record under:

```text
output/records/
```

The record contains:

```json
{
  "record": {},
  "fingerprint": "...",
  "tx_hash": "..."
}
```

---

## 13. Automatic Verification

CinU automatically performs four checks.

### Content Integrity

```text
Current SHA-256 == Recorded SHA-256
```

### Local Fingerprint

```text
Recomputed fingerprint == Saved fingerprint
```

### Polygon Verification

CinU retrieves the transaction data and checks:

```text
On-chain fingerprint == Saved fingerprint
```

### Blockchain Integrity

The blockchain verification must succeed.

A successful verification looks like:

```text
AUTOMATIC VERIFICATION

✓ Content file matches recorded SHA-256
✓ Local record fingerprint is valid
✓ Local fingerprint matches Polygon Amoy
✓ Blockchain record is intact

Verification:  ✅ VERIFIED
```

---

## 14. Complete Pipeline

Run:

```powershell
python -m app.pipeline
```

The pipeline has seven stages:

```text
[1/7] Building authorized face registry
[2/7] Scanning input image
[3/7] Searching public web content
[4/7] Downloading discovered content
[5/7] Creating content fingerprint
[6/7] Recording fingerprint on Polygon Amoy
[7/7] Automatically verifying
```

---

## 15. Recommended Live Hackathon Demo

The current implementation supports a dynamic demonstration.

### Step 1 — Add an identity

```powershell
python -m app.add_demo
```

For example:

```text
Profile ID: demo_06
Display name: Demo Person 06
Search query: Demo Person 06
Path to face image: <image path>
```

CinU creates:

```text
data/demo_06/
├── face.jpg
└── profile.json
```

### Step 2 — Select the input

```powershell
python -m app.select_input
```

Choose:

```text
Demo Person 06
```

CinU copies the selected image to:

```text
input/test.jpg
```

### Step 3 — Run CinU

```powershell
python -m app.pipeline
```

At startup CinU rebuilds the registry and therefore includes the newly added identity.

### Step 4 — Show verification

The final screen should show:

```text
✓ Content file matches recorded SHA-256
✓ Local record fingerprint is valid
✓ Local fingerprint matches Polygon Amoy
✓ Blockchain record is intact

Verification:  ✅ VERIFIED
```

This is a genuine dynamic workflow rather than a pre-generated result.

---

## 16. Example Successful Result

A successful run produces output similar to:

```text
======================================================================
                    CIN-U COMPLETE
======================================================================

Identity:      Demo Person 01
Profile ID:    demo_01
Similarity:    1.0000
Social results: 385
Best platform: Instagram
Content hash:  d4f604f68c9b5d78b18a36fa05e11559213932f36ee26fde8c41a32171621296
Fingerprint:   931f0c284bd0a482caddd9388ee8679af65a15e6ff1c2f1bf64af37d471356f1
TX Hash:       a0f66d842642cedf39b9460ec7c4a423915acbef30375df73b3118f4cb4e44bc

Verification:  ✅ VERIFIED
```

---

## 17. Environment Variables

Create a local `.env` file:

```env
SERPAPI_KEY=your_serpapi_key
POLYGON_RPC_URL=your_polygon_amoy_rpc_url
PRIVATE_KEY=your_wallet_private_key
BLOCKCHAIN_ADDRESS=your_wallet_address
```

### Security

Never commit `.env` to GitHub.

The `.gitignore` excludes:

```text
.env
.venv/
output/
input/
data/*/face.jpg
```

Never expose private keys or API keys in the repository.

---

## 18. Installation

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## 19. Useful Commands

### Add identity

```powershell
python -m app.add_demo
```

### Select input

```powershell
python -m app.select_input
```

### Build registry manually

```powershell
python -m app.registry_test
```

This is normally unnecessary because `app.pipeline` now rebuilds the registry automatically.

### Run complete pipeline

```powershell
python -m app.pipeline
```

### Component tests

```powershell
python -m app.search_test
python -m app.verify_test
python -m app.blockchain_test
```

---

## 20. Design Principles

### Authorized identities

Face matching is performed against an authorized registry of demo identities.

### No face data on-chain

Images and face embeddings are not stored on the blockchain.

### Hash instead of raw content

The blockchain stores the cryptographic fingerprint rather than the image.

### Reproducible verification

The fingerprint can be recomputed and compared with the recorded blockchain transaction.

### Transparent audit trail

The system links:

```text
Content
→ Content Hash
→ Record
→ Fingerprint
→ Blockchain Transaction
```

---

## 21. Limitations

CinU is a hackathon prototype.

- Face recognition depends on image quality, pose, lighting, and the underlying model.
- Google Lens results can change over time.
- Public search results do not prove ownership of a social-media account.
- A face match does not prove the authenticity of online content.
- Blockchain verification proves integrity of the recorded fingerprint, not the truth of the underlying content.
- Polygon Amoy is a testnet.
- The current application is a CLI prototype rather than a production application.

---

## 22. Privacy and Responsible Use

CinU should only be demonstrated with identities and images for which appropriate authorization exists.

Do not use the prototype to identify unknown people without consent or authorization.

Do not store face embeddings or personal images on-chain.

Keep API keys and wallet private keys outside the repository.

---

## 23. Hackathon Summary

CinU demonstrates:

```text
1. Add an authorized identity
2. Select an input image
3. Dynamically rebuild the face registry
4. Detect the face
5. Match the authorized identity
6. Search public web content
7. Discover relevant social content
8. Download discovered content
9. Generate SHA-256 content hash
10. Generate cryptographic fingerprint
11. Record fingerprint on Polygon Amoy
12. Retrieve blockchain transaction data
13. Recompute and compare fingerprints
14. Verify content integrity
15. Display VERIFIED
```

The key demonstration is that a newly added authorized identity can be introduced during the demo, automatically included in the registry, processed through the complete search and verification pipeline, and independently verified against the Polygon Amoy record.
