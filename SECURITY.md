# KALVETTU – Security & Moderation Architecture

## Overview
KALVETTU is a digital heritage platform dedicated to preserving and exploring verified Tamil temple inscriptions. Epigraphic integrity, data authenticity, and server-side confidentiality are critical requirements.

This document outlines the multi-layered security and moderation controls implemented across the frontend (React + TypeScript), backend (FastAPI + Python), and database/storage layer (Supabase PostgreSQL & Supabase Storage).

---

## 1. Zero-Trust Architecture for AI & Provenance Boundary

### 1.1 Verified vs. Draft Distinction
- **Authoritative Data**: Temples, inscriptions, and rulers ingested from ASI, Epigraphia Indica, and South Indian Inscriptions (SII) are marked `verified=true` and `verification_status='VERIFIED'`.
- **AI-Assisted Contributions**: Any record generated via the "Add a Kalvettu (AI)" ingestion pipeline is strictly tagged `verified=false` and `verification_status='DRAFT'`.
- **Public Visibility Guarantee**: The public frontend and default gallery/explorer endpoints (`/api/temples`, `/api/inscriptions`, `/api/search`) query **only** verified records. Draft records are stored with pending status and require human epigrapher approval before publication.

### 1.2 Hallucination Prevention
- AI chat interactions via the "Ask the Archive" tab use Retrieval-Augmented Generation (RAG) strictly anchored to verified database context.
- When an entity or query is unknown, the system explicitly returns authoritative missing-data responses (e.g., *"No verified temple record found in the Kalvettu archive"* or *"Information not currently available"*) rather than fabricating historical accounts.

---

## 2. Server-Side Secret Management

- **No Client Leakage**: All third-party AI keys (Groq, Cerebras, OpenRouter, Google Gemini), Supabase Service Role credentials, and PostgreSQL connection URIs are stored exclusively on the server in `python_backend/.env`.
- **Frontend Isolation**: The React/Vite frontend communicates solely with the FastAPI backend through `/api/*` endpoints. No service role keys, database connection strings, or LLM keys are ever exposed in client bundles or environment variables.
- **Repository Hygiene**: `.env` is ignored in `.gitignore`, and `.env.example` contains only non-sensitive placeholder variables.

---

## 3. Database Security & Row-Level Security (RLS)

- **PostgreSQL Connection Security**: Database connections utilize SSL/TLS (`sslmode=require`) against Supabase PostgreSQL.
- **Row-Level Security (RLS)**:
  - Tables `sources`, `dynasties`, `rulers`, `districts`, `temples`, `inscriptions`, `inscription_locations`, `images`, and `historical_events` have Row-Level Security enabled.
  - Public `anon` role is granted `SELECT` permission **only** on rows where `verified = true`.
  - Service role and authenticated administrator connections have full write and update privileges.
  - Audit logs (`audit_logs`) are append-only.

---

## 4. File Upload & Storage Security

- **Magic Byte Verification**: File uploads do not rely on client-provided MIME types or file extensions. The backend inspects the initial bytes to verify true image signatures:
  - JPEG: `\xff\xd8\xff`
  - PNG: `\x89PNG\r\n\x1a\n`
  - WebP: `RIFF....WEBP`
- **Size Limits**: Enforces a strict 10MB maximum file size limit.
- **Storage Isolation**: Images are written to public Supabase Storage buckets (`temples` and `inscriptions`) using randomly generated UUIDs (e.g., `uploads_<uuid>.jpg`). Client filenames are never used as storage keys, preventing path traversal attacks.

---

## 5. Server-Side Request Forgery (SSRF) Prevention

The external data service (`services/external_data.py`) queries external APIs (Wikimedia Commons, Wikidata). To prevent SSRF:
- **Domain Allowlist**: Only explicitly whitelisted hosts are reachable:
  - `commons.wikimedia.org`
  - `upload.wikimedia.org`
  - `www.wikidata.org`
  - `query.wikidata.org`
  - `asi.nic.in`
  - `whc.unesco.org`
  - `archive.org`
- **IP Address Validation**:
  - Rejects localhost (`localhost`, `127.0.0.1`, `::1`).
  - Rejects RFC 1918 private IP ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
  - Rejects link-local and cloud metadata addresses (e.g., `169.254.169.254`).

---

## 6. Rate Limiting & DoS Defense

- **Sliding-Window Rate Limiting**: All AI endpoints (`/api/ai/ask`, `/api/ai/chat`, `/api/ai/translate`, `/api/ai/extract`, `/api/ai/ingest`) are protected by IP-based sliding-window rate limiters to prevent API credit exhaustion and Denial-of-Service attacks.
- **HTTP 429 Responses**: Clients exceeding thresholds receive standard HTTP 429 Too Many Requests status codes with informative headers.

---

## 7. HTTP Security Headers & CORS

The FastAPI application enforces strict production headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- **CORS**: Restricted strictly to configured origins (`http://localhost:5173`, `http://localhost:3000`, `http://127.0.0.1:5173`), prohibiting insecure wildcard origins with credentials.

---

## 8. Audit Logging

Any modification, draft creation, or administrative action is logged to the `audit_logs` table with:
- Actor / Ingestion agent identifier
- Action type (`DRAFT_CREATED`, `RECORD_VERIFIED`, `IMAGE_UPLOADED`)
- Record type and unique ID
- Timestamp
