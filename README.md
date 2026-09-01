# Kalvettu — Digital Archive of Tamil Temple Inscriptions

A production-quality web application for a digital Tamil heritage project focused on
**Tamil temple inscriptions (கல்வெட்டு / Kalvettu)**. It connects the physical temple →
the exact inscription location → the original image → the transcription → the translation →
the historical meaning → the authoritative source.

> **Core principle: nothing is invented.** Every inscription retains its publication
> reference (SII volume/number, ARE number, or Epigraphia Indica). Where a fact,
> translation, image, or physical location cannot be verified from a primary/authoritative
> source, it is marked as *not recorded* rather than guessed.

---

## Required software

Before running anything, install the following tools:

| Tool | Version | Why | Install |
|------|---------|-----|---------|
| **Java (JDK)** | 21 | Runs the Spring Boot backend | https://adoptium.net (Temurin 21) or open in Spring Tool Suite |
| **Maven** | 3.9+ | Builds/launches the backend | `choco install maven` (Windows) or https://maven.apache.org |
| **Node.js** | 18 / 20 / 22 LTS | Runs the Vite/React frontend | https://nodejs.org (includes `npm`) |
| **Spring Tool Suite (STS)** | 4.x *(optional)* | IDE — bundles its own Java & Maven | https://spring.io/tools |
| **PostgreSQL** *(optional — production only)* | 14+ | Real database backend | `docker compose up -d` in `backend/`, or https://www.postgresql.org |

> Not strictly required: PostgreSQL. The app ships with **H2 in PostgreSQL-compatibility mode**,
> so a fresh clone runs end-to-end with just JDK + Maven + Node.

---

## Running the project (step by step)

### 1. Get the code

```bash
git clone https://github.com/aKash-S19/Inscription.git
cd Inscription
```

### 2. Start the backend (Spring Boot, port 8080)

```bash
cd backend
mvn spring-boot:run
```

- On first start it seeds data from `src/main/resources/data/dataset.json` (idempotent).
- If port 8080 is already in use, either free it or override the port:
  ```bash
  # PowerShell:
  $env:SERVER__PORT = "8081"; mvn spring-boot:run
  # Bash/macOS/Linux:
  SERVER__PORT=8081 mvn spring-boot:run
  ```
- **In STS:** `File > Import > Existing Maven Projects`, select the `backend` folder, then
  right-click the project → `Run As > Spring Boot App`.

### 3. Start the frontend (Vite, port 5173)

```bash
cd frontend
npm install
npm run dev
```

- Open http://localhost:5173 — the Vite dev server proxies `/api` to the backend on :8080.

### 4. Open the app

- Frontend (dev): http://localhost:5173
- Backend API: http://localhost:8080/api
- H2 console: http://localhost:8080/h2-console (JDBC URL `jdbc:h2:mem:kalvettu`, user `SA`)

---

## Tech stack

| Layer      | Technology |
|------------|------------|
| Frontend   | React 18 + TypeScript + Vite + Tailwind CSS |
| Backend    | Spring Boot 3.3 + Java 21 (REST API, JPA) |
| Database   | PostgreSQL (genuine DDL in `schema.sql`); runs out-of-the-box on H2 in PostgreSQL-compatibility mode |
| Maps       | Leaflet + OpenStreetMap (react-leaflet) |

## Screens

1. **Home** — hero + search, featured temples, explore by dynasty/district, featured inscriptions.
2. **Temple Gallery** — real photographs, search & filters (district/dynasty), verified cards.
3. **Temple Details** — overview, history, architecture, inscriptions, gallery, map, references.
4. **Inscription Explorer** — search + filter by temple / dynasty / ruler / district; thumbnails.
5. **Inscription Details** — original image, identification, transcription, translation, simple
   explanation, historical significance, and the cited source.
6. **Interactive Temple Map** — real temple coordinates (Leaflet/OSM); in-temple schematic of
   *verified* inscription locations that open the inscription. No invented locations.
7. **Explore by Dynasty / District** — Tamil Nadu districts + dynasty explorer (verified only).
8. **Timeline** — temples and rulers in chronological order.
9. **Sources / About** — project purpose, data policy, and authorities used.

---

## AI features (Kalvettu AI)

The project includes an optional AI layer powered by **Google Gemini** (via the
Gemini REST API). It is fully disabled until you supply an API key — the rest of
the app runs unaffected.

| AI feature | Endpoint | What it does |
|------------|----------|--------------|
| **Grounded chat assistant** | `POST /api/ai/chat` | Answers questions about temples, inscriptions, rulers and dynasties **strictly from the verified archive data** (retrieval-grounded); refuses to invent facts not in the context. Can answer in any language. |
| **Translate & explain a kalvettu** | `POST /api/ai/translate` | Faithfully translates any Tamil/Grantha kalvettu text into a chosen language and gives a plain-language explanation of its meaning. |
| **AI data ingestion** | `POST /api/ai/ingest` | Reads a photo (or pasted text) of an inscription with Gemini vision and outputs a structured draft record (title, language, script, translation, explanation, significance, ruler) for review. |

The UI lives at **`/ai`** (linked from the navbar) with tabs for chat, translate and ingest.

### Enabling the AI (set a Gemini API key)

1. Get a key: https://aistudio.google.com/apikey
2. Set it as an environment variable before starting the backend:

```bash
# PowerShell
$env:KALVETTU_AI_GEMINI_KEY = "your-key-here"
$env:KALVETTU_AI_GEMINI_MODEL = "gemini-2.0-flash"   # optional
mvn spring-boot:run

# Bash / macOS / Linux
export KALVETTU_AI_GEMINI_KEY="your-key-here"
export KALVETTU_AI_GEMINI_MODEL="gemini-2.0-flash"   # optional
mvn spring-boot:run
```

3. Without a key, AI endpoints return `503 "AI is not configured"`; set the key and restart.

> **Accuracy policy:** the chat assistant is grounded in the verified dataset and is
> instructed never to invent inscriptions, rulers, dates, translations or sources.
> AI translations / ingestion output is a **draft** — treat it as unverified until it
> matches a citable source (SII/ARE/etc.).

---

## Quick start (zero external install)

The backend uses **H2 in PostgreSQL compatibility mode** by default, so the whole stack runs
with no database server installed.

### 1. Backend (port 8080)

```bash
cd backend
# On Windows use the bundled mvn wrapper if needed; otherwise:
mvn spring-boot:run
# If an environment variable forces the port (e.g. SERVER__PORT), override it:
SERVER__PORT=8080 mvn spring-boot:run
```

Seed data is loaded from `backend/src/main/resources/data/dataset.json` + verified Wikimedia
Commons images (`data/commons_images.json`) on first start (idempotent).

### 2. Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the Vite dev server proxies `/api` to the backend on :8080.

---

## Production: real PostgreSQL

The DDL in `backend/src/main/resources/schema.sql` is genuine PostgreSQL. To run against a real
PostgreSQL server:

```bash
# create a database + role
createdb kalvettu
# then run the backend with the postgres profile:
mvn spring-boot:run -Dspring-boot.run.profiles=postgres
# or with env vars:
KALVETTU_DB_URL=jdbc:postgresql://localhost:5432/kalvettu \
KALVETTU_DB_USER=kalvettu KALVETTU_DB_PASSWORD=kalvettu \
mvn spring-boot:run -Dspring-boot.run.profiles=postgres
```

A `docker-compose.yml` is provided:

```bash
cd backend
docker compose up -d          # starts PostgreSQL on :5432
mvn spring-boot:run -Dspring-boot.run.profiles=postgres
```

### Serving the frontend from Spring Boot (single artifact)

```bash
cd frontend && npm run build          # outputs to frontend/dist
# copy the build into backend/src/main/resources/static, then:
cd backend && mvn spring-boot:run
# the app is then served at http://localhost:8080/  (API under /api)
```

---

## Data provenance

All textual data lives in `backend/src/main/resources/data/dataset.json`. Image URLs were
fetched from the **Wikimedia Commons API** and validated (HTTP 200) before inclusion, with
author + licence captured for attribution. Primary inscription sources include:

- **South Indian Inscriptions (SII)** — e.g. Vol. II (Rajarajesvaram temple, Thanjavur, ed. V. Venkayya, ASI NIS Vol. X, 1913); Vol. I (Pallava, Kanchipuram/Mamallapuram, ed. E. Hultzsch); Vol. XII (Chidambaram).
- **Annual Report on (South) Indian Epigraphy (ARE)** — e.g. Darasuram ARE 16–27 of 1908.
- **Epigraphia Indica**, **Archaeological Survey of India**, **UNESCO** (refs. 249 & 250), **Tamil Nadu Dept. of Archaeology**.

The original-script Tamil/Grantha text is cited to its publication rather than transcribed here,
to avoid propagating OCR errors; English summaries/translations are quoted from the cited editors.

## Project layout

```
backend/
  src/main/java/com/heritage/kalvettu/{domain,repository,service,web,dto,seed,config}
  src/main/resources/{application.yml, schema.sql, data/dataset.json, data/commons_images.json}
frontend/
  src/{components,pages,services,types}
  src/pages/*  (Home, TempleGallery, TempleDetails, InscriptionExplorer,
                InscriptionDetails, InteractiveMap, Explore, Timeline, About)
```

## Notes & limitations

- The dataset is intentionally **small and verified** (6 temples, 11 inscriptions). It is designed
  to grow as more records are verified — add entries to `dataset.json` and restart.
- In-temple map markers are an **indicative schematic**, not an authoritative temple plan; the
  authoritative plans are not redistributed. Every marker still links to its verified source.
- Photographs are hot-linked from Wikimedia Commons; if a file is later renamed upstream, update
  `data/commons_images.json` (re-run the Commons fetch script in `research/`).
