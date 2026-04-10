# SignalRank

SignalRank is a decision-intelligence API that ingests unstructured customer feedback and transforms it into ranked, actionable insights.

Instead of raw dashboards, SignalRank answers: **"What should I fix right now?"**

---

## How it works

1. Feedback arrives via API request or CSV upload
2. Each item is stored in PostgreSQL (structured metadata) and MongoDB (raw payload)
3. An enrichment service classifies the message — detecting sentiment and assigning an issue label (billing, support, onboarding, etc.)
4. The enrichment result is written back to both stores
5. `GET /api/v1/insights/issues` returns issues ranked by negative mention count

---

## Architecture

```text
Client / CSV Upload
        │
        ▼
  FastAPI Service
        │
   ┌────┴────┐
   ▼         ▼
PostgreSQL  MongoDB     ←── enrichment results, raw payloads
(feedback   (raw docs,
 metadata)   enrichment)
        │
        ▼
  External Enrichment API  (or built-in mock for local dev)
```

---

## Tech stack

| Layer | Technology |
| --- | --- |
| API | Python 3.11, FastAPI |
| Relational store | PostgreSQL 16, SQLAlchemy |
| Document store | MongoDB 7, PyMongo |
| Enrichment | Configurable external HTTP API (mock included) |
| Containerization | Docker, Docker Compose |
| Deployment | Kubernetes via Helm |
| Testing | pytest, SQLite in-memory |

---

## Project structure

```text
signalrank-repo/
├── app/
│   ├── core/
│   │   ├── config.py        # pydantic-settings, env-based config
│   │   ├── logging.py       # structured logging setup
│   │   └── security.py      # API key header validation
│   ├── models/
│   │   └── feedback.py      # SQLAlchemy Feedback model
│   ├── repos/
│   │   ├── mongo_repo.py    # MongoDB insert operations
│   │   └── postgres_repo.py # Postgres CRUD operations
│   ├── routes/
│   │   ├── feedback.py      # POST /api/v1/feedback
│   │   ├── health.py        # GET /health
│   │   ├── insights.py      # GET /api/v1/insights/issues
│   │   └── upload.py        # POST /api/v1/upload/csv
│   ├── services/
│   │   ├── enrichment.py    # calls external API, falls back to mock
│   │   ├── ingestion.py     # orchestrates feedback + enrichment flow
│   │   └── ranking.py       # aggregates and sorts issue summaries
│   ├── tests/
│   │   ├── conftest.py      # SQLite fixture, MongoDB mocks
│   │   ├── test_feedback.py
│   │   ├── test_health.py
│   │   ├── test_insights.py
│   │   └── test_upload.py
│   ├── db_mongo.py          # MongoDB client and collection handles
│   ├── db_postgres.py       # SQLAlchemy engine and session factory
│   ├── dependencies.py      # FastAPI dependency injection
│   ├── main.py              # app factory and router registration
│   └── schemas.py           # Pydantic request/response models
├── data/
│   └── sample_feedback.csv  # 15-row sample for local testing
├── helm/
│   └── signalrank/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/       # Deployment, Service, Ingress, Secret
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── start.sh
```

---

## Quick start

### 1. Configure environment

```bash
cp .env.example .env
```

Defaults in `.env.example` are sufficient for local development. The enrichment service automatically falls back to a built-in mock when `ENRICHMENT_API_URL` is set to the example value.

### 2. Start the stack

```bash
docker compose up --build
```

This starts:

| Service | URL |
| --- | --- |
| API | http://localhost:8000 |
| Interactive docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| MongoDB | localhost:27017 |

Docker Compose waits for Postgres and MongoDB health checks to pass before starting the API container.

---

## Authentication

All routes except `GET /health` require an `X-Api-Key` header.

```bash
-H "X-Api-Key: change-me"
```

The key is set via the `API_KEY` environment variable (default: `change-me`).

---

## API reference

### Health check

```http
GET /health
```

```json
{ "status": "ok" }
```

No authentication required.

---

### Submit feedback

```http
POST /api/v1/feedback
```

**Request body:**

```json
{
  "customer_id": 123,
  "product_id": 88,
  "channel": "email",
  "message": "Charged twice for my order",
  "event_date": "2026-04-01"
}
```

| Field | Type | Notes |
| --- | --- | --- |
| `customer_id` | integer | required |
| `product_id` | integer | required |
| `channel` | string | 2–50 characters |
| `message` | string | minimum 3 characters |
| `event_date` | date | `YYYY-MM-DD` |

**Response:**

```json
{
  "id": 1,
  "customer_id": 123,
  "product_id": 88,
  "channel": "email",
  "message": "Charged twice for my order",
  "sentiment": "negative",
  "issue_label": "billing",
  "event_date": "2026-04-01"
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: change-me" \
  -d '{
    "customer_id": 123,
    "product_id": 88,
    "channel": "email",
    "message": "Charged twice for my order",
    "event_date": "2026-04-01"
  }'
```

---

### Upload CSV

```http
POST /api/v1/upload/csv
```

Accepts a `.csv` file. Each row is processed through the same enrichment pipeline as a single feedback submission. Rows that fail validation are counted but do not abort the upload.

**Response:**

```json
{
  "rows_received": 15,
  "rows_processed": 14,
  "rows_failed": 1
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/v1/upload/csv \
  -H "X-Api-Key: change-me" \
  -F "file=@data/sample_feedback.csv"
```

**CSV format:**

```csv
customer_id,product_id,channel,message,event_date
123,88,email,"Charged twice for my order",2026-04-01
124,88,chat,"Support took too long to respond",2026-04-02
125,90,email,"Onboarding was confusing",2026-04-02
```

Required columns: `customer_id`, `product_id`, `channel`, `message`, `event_date`

---

### Ranked issue insights

```http
GET /api/v1/insights/issues
```

Returns all feedback grouped by issue label and ranked by negative mention count descending.

**Response:**

```json
[
  {
    "issue_label": "billing",
    "total_mentions": 12,
    "negative_mentions": 10,
    "channels": ["chat", "email", "phone"]
  },
  {
    "issue_label": "support",
    "total_mentions": 8,
    "negative_mentions": 6,
    "channels": ["chat", "email"]
  },
  {
    "issue_label": "onboarding",
    "total_mentions": 5,
    "negative_mentions": 3,
    "channels": ["email"]
  }
]
```

**Example:**

```bash
curl http://localhost:8000/api/v1/insights/issues \
  -H "X-Api-Key: change-me"
```

---

## Enrichment

The enrichment service classifies each feedback message for sentiment and issue label.

**Sentiment values:** `negative`, `neutral`

**Issue label values:** `billing`, `support`, `onboarding`, `pricing`, `other`

### Configuring an external provider

Set these environment variables to connect to a real NLP API:

```env
ENRICHMENT_API_URL=https://your-provider.com/analyze
ENRICHMENT_API_KEY=your_key_here
```

The service sends:

```json
{ "text": "<message>" }
```

And expects back:

```json
{
  "sentiment": "negative",
  "issue_label": "billing"
}
```

### Local mock

When `ENRICHMENT_API_URL` contains `example.com`, the service uses a built-in keyword classifier. This is the default for local development and tests — no external dependency required.

---

## Data model

### PostgreSQL — `feedback` table

| Column | Type | Description |
| --- | --- | --- |
| `id` | integer | primary key |
| `customer_id` | integer | indexed |
| `product_id` | integer | indexed |
| `channel` | varchar(50) | source channel |
| `message` | text | raw feedback text |
| `sentiment` | varchar(50) | set after enrichment |
| `issue_label` | varchar(100) | set after enrichment |
| `event_date` | date | when the feedback occurred |
| `created_at` | timestamptz | insert time |

### MongoDB collections

| Collection | Contents |
| --- | --- |
| `raw_feedback` | original payload as submitted |
| `enrichment_results` | full enrichment API response per feedback item |
| `issue_snapshots` | periodic issue summary snapshots (for trend analysis) |

---

## Configuration

All values can be set via environment variables or a `.env` file.

| Variable | Default | Description |
| --- | --- | --- |
| `API_KEY` | `change-me` | header auth key |
| `POSTGRES_URL` | `postgresql+psycopg2://postgres:postgres@postgres:5432/signalrank` | SQLAlchemy connection string |
| `MONGO_URL` | `mongodb://mongo:27017` | PyMongo connection string |
| `MONGO_DB_NAME` | `signalrank` | MongoDB database name |
| `ENRICHMENT_API_URL` | `https://example.com/analyze` | enrichment endpoint |
| `ENRICHMENT_API_KEY` | `replace-me` | enrichment auth token |
| `REQUEST_TIMEOUT_SECONDS` | `20` | HTTP timeout for enrichment calls |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `API_PREFIX` | `/api/v1` | route prefix |

---

## Testing

Tests use an in-memory SQLite database and mocked MongoDB collections — no running services required.

```bash
pytest
```

```text
17 passed in 0.08s
```

Test coverage includes:

- Feedback submission — success, label routing, auth enforcement, input validation
- CSV upload — full success, partial row failures, missing columns, wrong file type
- Issue insights — empty state, ranking correctness, response shape, auth enforcement
- Health check

---

## Deployment

### Docker

```bash
docker build -t signalrank .
docker run -p 8000:8000 --env-file .env signalrank
```

### Helm (Kubernetes)

```bash
# Install
helm install signalrank ./helm

# Upgrade
helm upgrade --install signalrank ./helm
```

Configure image, replica count, ingress, and secrets in [helm/signalrank/values.yaml](helm/signalrank/values.yaml).

---

## Roadmap

- Embedding-based issue clustering
- Trend detection over time windows
- Impact scoring (churn likelihood, revenue exposure)
- Slack and email alert integrations
- Lightweight frontend
- Multi-tenant support

---

## Author

Zachary Ginsburg  

---

## License

MIT
