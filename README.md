# CinU

## Content Integrity & Identity Verification System

CinU is a proof-of-concept system that combines face encoding, genuine reverse-image search, content fingerprinting, and blockchain verification into a single pipeline.

The system demonstrates how publicly discoverable content can be located through a genuine visual search process and then converted into a tamper-evident, verifiable record using SHA-256 and the Polygon Amoy blockchain.

> CinU is a hackathon proof of concept. It does not claim to prove ownership, authorship, or identity from a social-media result.

---

## How CinU Works

The complete pipeline is:

```text
Input Face Image
       ↓
Face Detection & Encoding
       ↓
Authorized Identity Matching
       ↓
Google Lens Reverse-Image Search
       ↓
Genuine Web / Social Result
       ↓
Content SHA-256
       ↓
Canonical Metadata Record
       ↓
Record Fingerprint
       ↓
Polygon Amoy Blockchain
       ↓
Independent Re-Hashing
       ↓
On-Chain Verification
       ↓
       VERIFIED


## Core Features

### 1. Face Detection & Encoding

CinU uses InsightFace to:

• Detect faces in an input image
• Generate face embeddings
• Compare the embedding against an authorized demo registry
• Identify the matching authorized demo profile

The system does not store face images or embeddings on the blockchain.

### 2. Genuine Reverse-Image Search

After an authorized face is matched, CinU sends the relevant image to SerpApi and performs a Google Lens search.

The search supports:

• Exact matches
• Visual matches
• Multiple web platforms
• Social-media sources such as Instagram, Reddit, Facebook, X, TikTok, YouTube and LinkedIn

The result is not hardcoded or pre-selected.

The platform returned by the search can vary depending on the actual search results.

### 3. Content Fingerprinting

When a result is discovered, CinU creates a SHA-256 hash of the downloaded content artifact.

A canonical metadata record is then created containing information such as:

• Platform
• Title
• Match type
• Content hash

The canonical record is hashed again to create the final CinU fingerprint.

### 4. Blockchain Recording

The resulting fingerprint is recorded on the:

Polygon Amoy Testnet

The blockchain stores the fingerprint rather than the original image or face data.

This keeps the sensitive content off-chain while providing an immutable reference for later verification.

### 5. Independent Verification

CinU does not simply trust the locally stored JSON record.

During verification it:

1. Loads the original verification record
2. Reads the fingerprint stored in the Polygon transaction
3. Independently re-hashes the discovered content
4. Compares the actual content hash with the recorded content hash
5. Recalculates the canonical record fingerprint
6. Compares the calculated fingerprint with the on-chain fingerprint

If all checks succeed:
✓ Content file matches recorded SHA-256
✓ Local record fingerprint is valid
✓ Local fingerprint matches Polygon Amoy
✓ Blockchain record is intact

✅ VERIFIED

If the downloaded content is modified, the content hash changes and verification fails.

## Technology Stack

| Component                 | Technology            |
| ------------------------- | --------------------- |
| Programming Language      | Python                |
| Face Detection & Encoding | InsightFace           |
| Face Model Runtime        | ONNX Runtime          |
| Image Processing          | OpenCV                |
| Reverse Image Search      | SerpApi / Google Lens |
| Hashing                   | SHA-256               |
| Blockchain                | Polygon Amoy Testnet  |
| Blockchain Library        | Web3.py               |
| Configuration             | python-dotenv         |
| Interface                 | Command Line          |


## Project Structure

CinU/
│
├── app/
│   ├── main.py
│   ├── pipeline.py
│   ├── verify.py
│   │
│   ├── face/
│   │   ├── encoder.py
│   │   ├── registry.py
│   │   ├── matcher.py
│   │   └── profile.py
│   │
│   ├── search/
│   │   ├── serpapi_client.py
│   │   └── matcher.py
│   │
│   └── blockchain/
│       ├── fingerprint.py
│       ├── content_hash.py
│       ├── client.py
│       ├── record.py
│       ├── storage.py
│       └── verify.py
│
├── data/
│   ├── demo_01/
│   ├── demo_02/
│   └── demo_03/
│
├── input/
│   └── test.jpg
│
├── output/
│   ├── discovered_content.jpg
│   ├── face_registry.json
│   └── records/
│
├── tests/
│
├── requirements.txt
├── .gitignore
└── README.md

## Installation

Clone the repository:
git clone https://github.com/anu-rag-007/CinU
cd CinU

Create a virtual environment:
python -m venv .venv

Activate it on Windows PowerShell / Terminal:
.venv\Scripts\Activate.ps1

Install dependencies:
pip install -r requirements.txt

## Environment Configuration

Create a .env file in the project root:
SERPAPI_KEY=your_serpapi_key
POLYGON_RPC_URL=your_polygon_amoy_rpc_url
PRIVATE_KEY=your_test_wallet_private_key
BLOCKCHAIN_ADDRESS=your_wallet_address

## Important

Never commit .env or a private key to GitHub.

The project .gitignore excludes:
.env
.venv/
__pycache__/
output/

Use a dedicated test wallet for Polygon Amoy.

## Running CinU

Place the input image at:
input/test.jpg

Run the complete pipeline:
python -m app.pipeline

The pipeline will:

1. Detect and encode the face
2. Match it against the authorized demo registry
3. Perform a genuine Google Lens search
4. Select a discovered result
5. Download the discovered content artifact
6. Generate a SHA-256 content hash
7. Generate a canonical record fingerprint
8. Record the fingerprint on Polygon Amoy
9. Save the verification record locally


## Verification

After the pipeline completes, copy the generated transaction hash.

Run:
python -m app.verify <TX_HASH>

Example:
python -m app.verify 0x123456789...

CinU will independently verify:
Content
   ↓
SHA-256
   ↓
Metadata Record
   ↓
Fingerprint
   ↓
Polygon Amoy

A successful verification produces:
✅ VERIFIED

## Blockchain Design

CinU uses a lightweight fingerprint-based blockchain design.

The actual image/content remains off-chain.

Only the cryptographic fingerprint is recorded on Polygon Amoy.

Conceptually:
Discovered Content
       ↓
    SHA-256
       ↓
 Content Hash
       ↓
Canonical Record
       ↓
    SHA-256
       ↓
Record Fingerprint
       ↓
 Polygon Amoy

This provides a tamper-evident reference without placing the original content or face data on-chain.


## Security & Privacy Considerations

CinU is designed as a consent-based/authorized demonstration.

The face matching stage operates against a predefined authorized demo registry.

CinU does not attempt to identify arbitrary unknown people from a live public camera feed.

Face embeddings and images are not stored on the blockchain.

Private blockchain credentials are stored locally in .env and should never be committed to source control.


## Limitations

CinU is a proof of concept and has several limitations.

### Identity limitation

A face match only indicates similarity to an authorized demo profile. It does not prove that a discovered social-media account belongs to that person.

### Search limitation

Reverse-image search results depend on the external search provider and publicly indexed content.

A result may be related to the image without establishing ownership or authorship.

### Blockchain limitation

Blockchain verification proves that the recorded fingerprint has not changed.

It does not prove that the original content was truthful, authentic, legally owned, or created by a particular person.

### Content limitation

The current prototype stores the discovered content artifact locally and records its fingerprint on-chain.

A production system would require robust content storage, provenance, access control, and evidence-management mechanisms.

### Testnet limitation

The prototype uses Polygon Amoy Testnet and is intended for demonstration purposes rather than production deployment.


## Why Blockchain?

Traditional local records can be modified or deleted.

CinU creates a cryptographic fingerprint of the recorded evidence and anchors that fingerprint to a blockchain transaction.

This allows the system to later answer:

"Does the current content still produce the same fingerprint that was recorded?"

If yes:

Current Content
      ==
Recorded Fingerprint
      ==
Blockchain Fingerprint

      ↓

    VERIFIED

If the content changes, the fingerprint changes and the verification fails.


## Hackathon Scope

CinU demonstrates the following required concepts:

• Face detection and encoding
• Genuine reverse-image search
• Discovery of real web/social content
• Cryptographic content fingerprinting
• Blockchain recording
• Independent blockchain verification
• Tamper-evident evidence handling

No website is required for the prototype.

The complete demonstration is performed through the command line.

## Disclaimer

CinU is an experimental hackathon prototype intended to demonstrate technical feasibility.

It should not be used as a standalone system for identity verification, legal evidence authentication, surveillance, or attribution of social-media content.

Blockchain immutability applies to the recorded fingerprint, not to the truthfulness or ownership of the underlying content.

## Team TRICYCLE