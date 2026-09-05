# CinU

## Face ID + Blockchain Verification

CinU is a privacy-conscious prototype that combines **face recognition, public image/content search, cryptographic hashing, and blockchain verification** into a single command-line workflow.

The system is designed for an authorized/consent-based demonstration. It matches a face against a locally maintained registry of authorized demo profiles, searches the corresponding profile image using Google Lens through SerpApi, creates a cryptographic fingerprint of the discovered content and its metadata, records that fingerprint on the Polygon Amoy testnet, and finally verifies that the local record and discovered content have not been modified.

> **Important:** CinU does not claim that a blockchain transaction proves a person's identity, ownership of an image, or the truthfulness of a social-media post. The blockchain is used to prove the integrity of the fingerprint recorded by CinU.

---

# Table of Contents

1. [What CinU Does](#what-cinu-does)
2. [How It Works](#how-it-works)
3. [Main Features](#main-features)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Requirements](#requirements)
7. [Installation](#installation)
8. [Environment Configuration](#environment-configuration)
9. [Preparing a Demo Profile](#preparing-a-demo-profile)
10. [Running CinU](#running-cinu)
11. [Verification](#verification)
12. [How Blockchain Is Used](#how-blockchain-is-used)
13. [Fingerprint and Integrity Model](#fingerprint-and-integrity-model)
14. [Privacy and Security](#privacy-and-security)
15. [Limitations](#limitations)
16. [Troubleshooting](#troubleshooting)
17. [Hackathon Scope](#hackathon-scope)
18. [Disclaimer](#disclaimer)

---

# What CinU Does

CinU demonstrates an end-to-end verification pipeline:

```text
Authorized Face Image
        |
        v
Face Detection
        |
        v
Face Embedding
        |
        v
Authorized Profile Matching
        |
        v
Public Image Search
(Google Lens via SerpApi)
        |
        v
Best Search Result
        |
        v
Content SHA-256 Hash
        |
        v
Canonical Verification Record
        |
        v
SHA-256 Fingerprint
        |
        v
Polygon Amoy Blockchain
        |
        v
Local Verification
        |
        v
VERIFIED / FAILED
```

The system separates:

- **Identity matching** — whether an input face is similar to an authorized demo profile.
- **Content discovery** — whether a related image/content result can be found publicly.
- **Integrity verification** — whether the recorded content and metadata still match the fingerprint recorded on-chain.

---

# How It Works

CinU performs the following steps.

### 1. Load the authorized registry

CinU loads authorized demo profiles from:

```text
data/
```

Each profile contains metadata such as:

```json
{
  "profile_id": "demo_01",
  "display_name": "Demo Person 01",
  "search_query": "Demo Person 01"
}
```

The actual demo face images are kept locally and are intentionally excluded from Git.

### 2. Detect the face

The input image is processed using OpenCV and InsightFace.

The system detects:

- face bounding box
- detection confidence
- face embedding

### 3. Match against authorized profiles

The generated embedding is compared against the authorized face registry using cosine similarity.

CinU currently uses a configurable similarity threshold in the matcher.

A successful match identifies an authorized demo profile such as:

```text
demo_01
```

This is an **authorized demo identity**, not an attempt to identify an unknown person from the internet.

### 4. Search for related public content

After a profile is matched, CinU sends the authorized profile image to SerpApi's image-search endpoint and uses Google Lens to search for visually/exactly related public content.

The search can return results from different public platforms, including sources such as:

```text
Instagram
Reddit
Other indexed public sources
```

CinU does not hard-code a particular social-media platform.

### 5. Select the best result

The search matcher evaluates the returned results and selects the most relevant result.

The resulting metadata may include:

```text
Platform
Title
Match Type
Content URL / Redirect
```

If the external source does not expose a directly usable URL, CinU can retain the returned thumbnail/content artifact for the integrity demonstration.

### 6. Hash the discovered content

CinU calculates a SHA-256 hash of the discovered content.

Example:

```text
d4f604f68c9b5d78b18a36fa05e11559213932f36ee26fde8c41a32171621296
```

The hash acts as a cryptographic representation of the exact file.

If even a small part of the file changes, the SHA-256 hash changes.

### 7. Create a verification record

CinU creates a canonical record containing information such as:

```json
{
  "platform": "Instagram",
  "title": "Example result",
  "match_type": "exact_match",
  "content_hash": "..."
}
```

The record is serialized deterministically and hashed using SHA-256.

This produces the CinU fingerprint.

### 8. Record the fingerprint on Polygon

The fingerprint is recorded in a transaction on the:

```text
Polygon Amoy Testnet
```

CinU does **not** store face images or face embeddings on the blockchain.

Only the cryptographic fingerprint is recorded.

### 9. Verify the record

The verification process independently:

1. Loads the saved local record.
2. Reads the blockchain transaction.
3. Retrieves the on-chain fingerprint.
4. Re-hashes the discovered content.
5. Recalculates the local record fingerprint.
6. Compares the local fingerprint with the blockchain fingerprint.

If all checks match:

```text
VERIFIED
```

---

# Main Features

## Face Recognition

- Face detection using InsightFace.
- Face embeddings using the `buffalo_l` model.
- Authorized profile matching.
- Cosine similarity comparison.

## Public Image Search

- Uses SerpApi.
- Uses Google Lens.
- Supports exact and visual matching.
- Does not hard-code a single social-media platform.

## Cryptographic Integrity

- SHA-256 content hashing.
- Canonical JSON serialization.
- Deterministic record fingerprints.

## Blockchain Verification

- Polygon Amoy testnet.
- Web3.py integration.
- On-chain fingerprint recording.
- Independent verification against blockchain data.

## Privacy-Conscious Design

CinU does not store:

- Face embeddings on-chain.
- Face images on-chain.
- Private API keys in GitHub.
- Private credentials in the repository.

---

# Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Face Detection / Recognition | InsightFace |
| Inference Runtime | ONNX Runtime |
| Image Processing | OpenCV |
| Numerical Processing | NumPy |
| Public Image Search | SerpApi |
| Visual Search | Google Lens |
| Hashing | SHA-256 |
| Blockchain | Polygon Amoy |
| Blockchain Library | Web3.py |
| Configuration | python-dotenv |
| Interface | Command Line |

---

# Project Structure

```text
CinU/
|
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── pipeline.py
│   ├── verify.py
│   |
│   ├── face/
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   ├── encoder.py
│   │   ├── matcher.py
│   │   ├── profile.py
│   │   ├── registry.py
│   │   └── match_test.py
│   |
│   ├── search/
│   │   ├── __init__.py
│   │   ├── matcher.py
│   │   ├── serpapi_client.py
│   │   ├── profile_search_test.py
│   │   └── ...
│   |
│   ├── blockchain/
│   │   ├── client.py
│   │   ├── content_hash.py
│   │   ├── contract.py
│   │   ├── fingerprint.py
│   │   ├── record.py
│   │   ├── storage.py
│   │   ├── verify.py
│   │   └── ...
│   |
│   └── hashing/
│       └── fingerprint.py
|
├── data/
│   ├── demo_01/
│   │   └── profile.json
│   ├── demo_02/
│   │   └── profile.json
│   └── demo_03/
│       └── profile.json
|
├── input/
│   └── .gitkeep
|
├── output/
│   └── .gitkeep
|
├── tests/
│   ├── test_hashing.py
│   └── test_verification.py
|
├── contracts/
|
├── .gitignore
├── README.md
└── requirements.txt
```

---

# Requirements

Before installing CinU, make sure the system has:

- Python 3.10+ recommended
- Git
- Internet connection
- A SerpApi API key
- A Polygon Amoy RPC endpoint
- A funded Polygon Amoy wallet for transaction fees

A CUDA-capable GPU is **not required** for the current prototype because ONNX Runtime CPU execution is used.

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/anu-rag-007/CinU.git
cd CinU
```

## 2. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

You should see:

```text
(.venv)
```

at the beginning of your terminal prompt.

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

From the project root:

```bash
pip install -r requirements.txt
```

Verify the installation:

```bash
pip check
```

A successful installation should report:

```text
No broken requirements found.
```

---

# Environment Configuration

CinU requires environment variables for external services.

Create a file named:

```text
.env
```

in the project root.

Example:

```env
SERPAPI_KEY=your_serpapi_key

POLYGON_RPC_URL=your_polygon_amoy_rpc_url

PRIVATE_KEY=your_wallet_private_key

BLOCKCHAIN_ADDRESS=your_wallet_address
```

## Important

**Never commit `.env` to GitHub.**

The repository's `.gitignore` already excludes:

```text
.env
```

Do not share your private key publicly.

---

# Getting a SerpApi Key

Create an account with SerpApi and obtain an API key.

Place the key in:

```env
SERPAPI_KEY=your_key_here
```

CinU uses the key to perform the image-search request and Google Lens search.

---

# Polygon Amoy Configuration

CinU uses the Polygon Amoy testnet for the blockchain demonstration.

Your configuration should provide:

```env
POLYGON_RPC_URL=...
PRIVATE_KEY=...
BLOCKCHAIN_ADDRESS=...
```

The wallet must contain enough Polygon Amoy testnet funds to submit transactions.

Only use a **testnet wallet** for this project.

Do not use a wallet containing real mainnet funds.

---

# Preparing a Demo Profile

CinU uses an authorized local registry rather than attempting to identify arbitrary unknown people.

Each demo profile is stored under:

```text
data/
```

Example:

```text
data/
└── demo_01/
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

The face image:

```text
face.jpg
```

is intentionally ignored by Git because it is local demo data.

If you want to create your own authorized demo profile, create a new directory:

```text
data/demo_04/
```

and add:

```text
face.jpg
profile.json
```

Make sure the face image is used with appropriate consent.

---

# Running CinU

Place the input image in:

```text
input/
```

For example:

```text
input/test.jpg
```

Then run CinU from the project root:

```bash
python -m app.main
```

The pipeline will perform the complete workflow.

---

# Expected Pipeline

A successful run follows approximately this sequence:

```text
1. Loading authorized registry
2. Detecting and encoding input face
3. Matching authorized profile
4. Searching public content
5. Selecting best search result
6. Creating cryptographic fingerprint
7. Recording fingerprint on Polygon Amoy
8. Saving verification record
```

The exact output may vary depending on the search results returned by the external search service.

---

# Output Files

Generated runtime files are stored under:

```text
output/
```

Examples include:

```text
output/face_registry.json
output/face_1_embedding.npy
output/discovered_content.jpg
output/records/
```

These files are intentionally excluded from Git because they are generated/local runtime artifacts.

---

# Verification

After the main pipeline successfully records a fingerprint on Polygon Amoy, run:

```bash
python -m app.verify
```

The verification process checks:

```text
Local record
      |
      +-- Content SHA-256
      |
      +-- Record fingerprint
      |
      v
Polygon Amoy transaction
      |
      v
On-chain fingerprint
```

A successful verification should contain checks similar to:

```text
✓ Content file matches recorded SHA-256
✓ Local record fingerprint is valid
✓ Local fingerprint matches Polygon Amoy
✓ Blockchain record is intact

VERIFIED
```

---

# How Blockchain Is Used

CinU uses the blockchain as an **integrity anchor**.

The system does not put the complete record or media file on-chain.

Instead:

```text
Content
   |
   v
SHA-256
   |
   v
Canonical Record
   |
   v
SHA-256 Fingerprint
   |
   v
Polygon Amoy Transaction
```

The transaction contains the fingerprint as transaction data.

During verification:

```text
Local Fingerprint
       |
       v
     Compare
       ^
       |
Blockchain Fingerprint
```

If they match, the local record has the same cryptographic fingerprint that was recorded on-chain.

---

# Why Not Store the Image on Blockchain?

Storing images or face embeddings directly on a public blockchain would be inefficient and can create unnecessary privacy concerns.

CinU therefore uses:

```text
Off-chain:
- Images
- Face embeddings
- Search artifacts
- Local verification records

On-chain:
- Cryptographic fingerprint
```

This provides a lightweight integrity mechanism without putting biometric data on the blockchain.

---

# Fingerprint and Integrity Model

CinU uses deterministic JSON serialization before calculating the fingerprint.

Conceptually:

```text
record
  |
  v
JSON serialization
  |
  v
sorted keys
  |
  v
deterministic representation
  |
  v
SHA-256
  |
  v
fingerprint
```

For example:

```text
SHA256(canonical_record)
```

produces a hexadecimal fingerprint such as:

```text
931f0c284bd0a482caddd9388ee8679af65a15e6ff1c2f1bf64af37d471356f1
```

If the record changes:

```text
Original Record
      |
      v
Fingerprint A
```

becomes:

```text
Modified Record
      |
      v
Fingerprint B
```

Since:

```text
Fingerprint A != Fingerprint B
```

the modification can be detected.

---

# Privacy and Security

CinU is intentionally designed around an authorized demonstration model.

## Face Data

Face images and embeddings remain local.

They are not written to the blockchain.

## API Keys

API keys are loaded from `.env`.

They are not included in the repository.

## Private Keys

The Polygon private key is loaded from `.env`.

It must never be committed to GitHub or shared with other people.

## Blockchain

The blockchain stores only a cryptographic fingerprint rather than biometric data.

---

# Limitations

CinU is a hackathon prototype and has several limitations.

## 1. Face recognition is not perfect

Face recognition can produce false positives and false negatives.

The similarity threshold should therefore not be interpreted as absolute proof of identity.

## 2. Search results are not proof of ownership

Finding an image through Google Lens does not prove:

- who uploaded it
- who owns it
- who appears in it
- whether the post is authentic
- whether the content is manipulated

CinU treats search results as **discovered public content**, not as ground truth.

## 3. Search APIs can change

SerpApi and Google Lens responses may change over time.

External search results can disappear, change URLs, or become unavailable.

## 4. Social-media URLs may not always be directly accessible

Some search results may use redirect URLs or thumbnails rather than a directly accessible original post.

CinU retains the available search artifact for the integrity demonstration when necessary.

## 5. Blockchain does not prove truth

The blockchain proves that a particular fingerprint was recorded.

It does not prove that the underlying information is true.

For example:

```text
Blockchain proves:
"The fingerprint recorded today matches this record."

Blockchain does NOT prove:
"The information in this record is factually correct."
```

## 6. Polygon Amoy is a testnet

The project uses Polygon Amoy for demonstration purposes.

It should not be considered a production blockchain deployment.

---

# Troubleshooting

## `ModuleNotFoundError`

If you see an error such as:

```text
ModuleNotFoundError: No module named 'face'
```

make sure the project uses package imports from the project root.

For example:

```python
from app.face.encoder import FaceEncoder
```

Then run the application from the repository root:

```bash
python -m app.main
```

Do not run:

```bash
python app/main.py
```

unless the code has specifically been configured for direct script execution.

## `pip check` reports problems

Run:

```bash
pip install -r requirements.txt --upgrade
```

Then:

```bash
pip check
```

## SerpApi errors

Check:

```env
SERPAPI_KEY=...
```

Make sure:

- the key is valid
- the machine has internet access
- the SerpApi account has available usage

## Polygon connection errors

Check:

```env
POLYGON_RPC_URL=...
```

Also verify that:

- the RPC endpoint is valid
- the wallet private key is correct
- the wallet address is correct
- the wallet has Polygon Amoy testnet funds

## Insufficient blockchain funds

If a transaction fails because of insufficient funds, fund the wallet with Polygon Amoy testnet tokens and try again.

Never fund the project wallet with real mainnet assets for this demonstration.

## No face detected

Make sure the input image:

- contains a clearly visible face
- has reasonable lighting
- is not extremely blurry
- has sufficient resolution
- is compatible with the InsightFace detector

## No search result

Public search results are not guaranteed.

Possible reasons include:

- the image is not indexed
- the image has changed
- the search service returns different results
- the external platform restricts indexing
- API limits have been reached

---

# Running Tests

The repository contains tests for hashing and verification components.

Run:

```bash
python -m pytest
```

If `pytest` is not installed in your environment:

```bash
pip install pytest
```

Then run:

```bash
python -m pytest
```

---

# Recommended End-to-End Demo

For a hackathon demonstration, use the following sequence.

### Step 1

Clone the repository:

```bash
git clone https://github.com/anu-rag-007/CinU.git
cd CinU
```

### Step 2

Create and activate the virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 3

Install dependencies:

```powershell
pip install -r requirements.txt
```

### Step 4

Create `.env` with the required API and blockchain configuration.

### Step 5

Place an authorized demo input image at:

```text
input/test.jpg
```

### Step 6

Run:

```powershell
python -m app.main
```

### Step 7

Wait for the Polygon Amoy transaction to complete.

### Step 8

Run:

```powershell
python -m app.verify
```

### Step 9

Show the final:

```text
VERIFIED
```

result.

This demonstrates the complete flow:

```text
Face
 |
 v
Authorized Match
 |
 v
Public Search
 |
 v
Content Hash
 |
 v
Record Fingerprint
 |
 v
Polygon Amoy
 |
 v
Independent Verification
```

---

# Hackathon Scope

CinU was developed as a prototype demonstrating how biometric matching, public content discovery, cryptographic integrity, and blockchain anchoring can be combined into one workflow.

The implementation intentionally focuses on demonstrating the core technical concept rather than providing a production-ready identity verification service.

The current implementation is CLI-based and does not require a website.

---

# Security Notes

Before deploying or extending CinU:

- Never commit `.env`.
- Never commit private keys.
- Never place private keys directly inside Python source files.
- Never store biometric data on a public blockchain without appropriate legal and privacy review.
- Use consent-based/authorized datasets for demonstrations.
- Treat external search results as untrusted data.
- Validate all external API responses.
- Use a dedicated testnet wallet during development.

---

# Disclaimer

CinU is a technical prototype intended for authorized demonstrations, research, and hackathon evaluation.

It should not be used to identify unknown individuals, monitor people without consent, or make high-impact decisions based solely on face recognition or public search results.

A face match is not absolute proof of identity.

A search result is not proof of ownership or authenticity.

A blockchain fingerprint is not proof that the underlying information is true.

The blockchain component demonstrates **data integrity and tamper detection**, not factual verification.

---

# Repository

GitHub:

https://github.com/anu-rag-007/CinU

---

# CinU

**Face ID + Public Content Discovery + Cryptographic Fingerprinting + Blockchain Verification**
