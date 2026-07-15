# StartPitch API

Flask backend API for StartPitch — a platform connecting startup founders with investors and mentors. Handles auth, startup/pitch submissions, AI-assisted evaluations, investor matching, mentor bookings, deal rooms, messaging, and notifications.

> **Note:** Data models (users, startups, pitches, matches, etc.) are currently held in in-memory Python dicts/lists inside each route module — there is no database wired up yet. All data resets when the server restarts.

## Tech stack

- Python 3.12
- Flask 3
- flask-jwt-extended (auth)
- flask-bcrypt (password hashing)
- flask-cors
- gunicorn (production server)

## Getting started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

Run the development server:

```bash
python run.py
```

The API will be available at `http://127.0.0.1:5000`.

For production, the `Procfile` runs it via gunicorn:

```bash
gunicorn run:app
```

### Environment variables

| Variable                   | Description                     | Default          |
|----------------------------|---------------------------------|------------------|
| `SECRET_KEY`               | Flask secret key                | `dev-secret-key` |
| `JWT_SECRET_KEY`           | Secret used to sign JWTs        | `jwt-dev-secret` |
| `JWT_ACCESS_TOKEN_EXPIRES` | Access token lifetime (seconds) | `1800`           |
| `JWT_REFRESH_TOKEN_EXPIRES`| Refresh token lifetime (seconds)| `604800`         |

## Authentication

Most endpoints require a Bearer JWT access token, obtained from `/api/v1/auth/login` or `/api/v1/auth/register`:

```
Authorization: Bearer <access_token>
```

Endpoints under `/api/v1/admin` additionally require the JWT's `role` claim to be `admin`.

## Health check

| Method | Endpoint | Description                                |
|--------|----------|--------------------------------------------|
| GET    | `/health`| Liveness check, returns `{"status": "ok"}` |

## API Endpoints

All endpoints below are prefixed with `/api/v1` unless noted otherwise. 🔒 = requires `Authorization: Bearer <access_token>`. 🔒admin = also requires the JWT's `role` claim to be `admin`. Request/response bodies below are real examples captured from a running instance.

---

### Auth (`/api/v1/auth`)

#### POST `/auth/register` — Register a new user

```json
{
  "email": "founder@startpitch.dev",
  "password": "pw123",
  "role": "founder"
}
```

**Success response `201`**
```json
{
  "id": 1,
  "email": "founder@startpitch.dev",
  "role": "founder"
}
```

**Missing fields `400`**
```json
{
  "error": "email and password are required"
}
```

**Duplicate email `409`**
```json
{
  "error": "Email already registered"
}
```

---

#### POST `/auth/login` — Log in

```json
{
  "email": "founder@startpitch.dev",
  "password": "pw123"
}
```

**Success response `200`**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Invalid credentials `401`**
```json
{
  "error": "Invalid credentials"
}
```

---

#### POST `/auth/oauth/google` — Google OAuth (stub)

No request body needed.

**Response `200`**
```json
{
  "provider": "google",
  "status": "stub"
}
```

---

#### POST `/auth/oauth/linkedin` — LinkedIn OAuth (stub)

No request body needed.

**Response `200`**
```json
{
  "provider": "linkedin",
  "status": "stub"
}
```

---

#### POST `/auth/refresh` 🔒 (refresh token) — Get a new token pair

Send the **refresh token** (not the access token) as the Bearer token. No request body needed.

**Success response `200`**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Access token used instead of refresh token `422`**
```json
{
  "msg": "Only refresh tokens are allowed"
}
```

---

### Users (`/api/v1/users`)

#### GET `/users/me` 🔒 — Get the current authenticated user

No request body needed.

**Success response `200`**
```json
{
  "id": 1,
  "email": "founder@startpitch.dev",
  "role": "founder"
}
```

---

#### PATCH `/users/me` 🔒 — Update the current user's profile

```json
{
  "name": "Bob",
  "bio": "Serial founder"
}
```

**Success response `200`**
```json
{
  "updated": true,
  "profile": {
    "name": "Bob",
    "bio": "Serial founder"
  }
}
```

---

#### GET `/users/<user_id>/profile-completeness` 🔒 — Get profile completeness score

No request body needed.

**Success response `200`**
```json
{
  "user_id": 1,
  "score": 66
}
```

**Not found `404`**
```json
{
  "error": "User not found"
}
```

---

### Startups (`/api/v1/startups`)

#### POST `/startups` 🔒 — Create a startup

```json
{
  "name": "Acme",
  "sector": "fintech",
  "stage": "seed",
  "geography": "US",
  "check_size": "small"
}
```

**Success response `201`**
```json
{
  "id": 1,
  "name": "Acme",
  "sector": "fintech",
  "stage": "seed",
  "geography": "US",
  "check_size": "small"
}
```

---

#### GET `/startups/<startup_id>` 🔒 — Get a startup by ID

No request body needed.

**Success response `200`** — same shape as create.

**Not found `404`**
```json
{
  "error": "Startup not found"
}
```

---

#### PATCH `/startups/<startup_id>` 🔒 — Update a startup

```json
{
  "stage": "series-a"
}
```

**Success response `200`** — full startup object with the field merged in.

**Not found `404`**
```json
{
  "error": "Startup not found"
}
```

---

### Pitches (`/api/v1/pitches`)

#### POST `/pitches` 🔒 — Create a pitch

```json
{
  "title": "Acme Pitch",
  "summary": "sum",
  "startup_id": 1
}
```

**Success response `201`**
```json
{
  "id": 1,
  "title": "Acme Pitch",
  "summary": "sum",
  "content_url": null,
  "input_type": "form",
  "startup_id": 1
}
```

---

#### GET `/pitches` 🔒 — List pitches

Optional query params: `?startup_id=`, `?visibility=`

**Success response `200`**
```json
[
  {
    "id": 1,
    "title": "Acme Pitch",
    "summary": "sum",
    "content_url": null,
    "input_type": "form",
    "startup_id": 1
  }
]
```

---

#### GET `/pitches/<pitch_id>` 🔒 — Get a pitch by ID

**Success response `200`** — same shape as create. **Not found `404`**: `{"error": "Pitch not found"}`

---

#### POST `/pitches/<pitch_id>/versions` 🔒 — Add a new version to a pitch

```json
{
  "content_url": "https://storage.local/deck-v2.pdf"
}
```

**Success response `201`**
```json
{
  "id": 1,
  "pitch_id": 1,
  "content_url": "https://storage.local/deck-v2.pdf",
  "status": "queued"
}
```

**Pitch not found `404`**
```json
{
  "error": "Pitch not found"
}
```

---

#### GET `/pitches/<pitch_id>/versions` 🔒 — List versions of a pitch

**Success response `200`** — array of version objects (see above).

---

#### GET `/pitches/<pitch_id>/versions/<version_id>` 🔒 — Get a specific version

**Success response `200`** — single version object. **Not found `404`**: `{"error": "Version not found"}`

---

#### GET `/pitches/<pitch_id>/versions/<version_id>/status` 🔒 — Get processing status

**Success response `200`**
```json
{
  "status": "queued"
}
```

---

#### GET `/pitches/<pitch_id>/score-history` 🔒 — Get score history across versions

**Success response `200`**
```json
[
  {
    "version_id": 1,
    "overall_score": 71,
    "delta": 1
  }
]
```

---

### Evaluations (`/api/v1/evaluations`)

#### POST `/evaluations` 🔒 — Queue an AI evaluation job

```json
{
  "pitch_version_id": 1
}
```

**Response `202`** (job queued, processed asynchronously in a background thread)
```json
{
  "id": 1,
  "pitch_version_id": 1,
  "status": "processing"
}
```

---

#### GET `/evaluations/jobs/<job_id>` 🔒 — Get status/result of an evaluation job

**While processing `200`**
```json
{
  "id": 1,
  "pitch_version_id": 1,
  "status": "processing"
}
```

**Once done `200`** (a few seconds later)
```json
{
  "id": 1,
  "pitch_version_id": 1,
  "status": "done",
  "score": {
    "market": 78,
    "team": 82,
    "traction": 70,
    "financials": 73,
    "defensibility": 76,
    "clarity": 80,
    "overall": 76.5
  },
  "feedback": {
    "market": [
      {
        "claim": "Large target segment",
        "evidence_snippet_from_pitch": "Addressing mid-sized SaaS firms",
        "verdict": "reasonable"
      }
    ]
  }
}
```

**Not found `404`**
```json
{
  "error": "Job not found"
}
```

---

#### GET `/evaluations/<pitch_version_id>` 🔒 — Get the completed evaluation for a pitch version

**Success response `200`** — same shape as a "done" job above.

**Not ready yet `404`**
```json
{
  "error": "Evaluation not ready"
}
```

---

#### POST `/evaluations/<evaluation_id>/override` 🔒 — Manually override an evaluation

```json
{
  "overall": 85,
  "reason": "Reviewer adjusted after live Q&A"
}
```

**Success response `200`**
```json
{
  "updated": true,
  "evaluation": {
    "id": 1,
    "pitch_version_id": 1,
    "status": "done",
    "override": {
      "overall": 85,
      "reason": "Reviewer adjusted after live Q&A"
    }
  }
}
```

**Not found `404`**
```json
{
  "error": "Evaluation not found"
}
```

---

### Matching (`/api/v1`)

#### POST `/thesis` 🔒 — Create/update an investor's thesis

```json
{
  "investor_id": 1,
  "sector": "fintech",
  "stage": "seed",
  "geography": "US",
  "check_size": "small"
}
```

**Success response `201`** — echoes the thesis back with `investor_id` set.

**Non-integer `investor_id` `400`**
```json
{
  "error": "investor_id must be an integer"
}
```

---

#### GET `/thesis/<investor_id>` 🔒 — Get an investor's thesis

**Success response `200`** — same shape as create. **Not found `404`**: `{"error": "Thesis not found"}`

---

#### POST `/matches/recompute` 🔒 — Recompute all startup ↔ investor matches

No request body needed. Scores every startup against every stored thesis (40 pts sector match, 30 stage, 15 geography, 15 check size).

**Success response `200`**
```json
[
  {
    "id": 1,
    "investor_id": 1,
    "startup_id": 1,
    "score": 100,
    "rationale": {
      "sector": 40,
      "stage": 30,
      "geography": 15,
      "check_size": 15
    }
  }
]
```

---

#### GET `/matches/for-investor/<investor_id>` 🔒 — List matches for an investor

**Success response `200`** — array of match objects (see above).

---

#### GET `/matches/for-startup/<startup_id>` 🔒 — List matches for a startup

**Success response `200`** — array of match objects (see above).

---

#### GET `/matches/<match_id>/rationale` 🔒 — Get the rationale behind a match

**Success response `200`**
```json
{
  "sector": 40,
  "stage": 30,
  "geography": 15,
  "check_size": 15
}
```

**Not found `404`**
```json
{
  "error": "Match not found"
}
```

---

### Reputation (`/api/v1/reputation`)

#### GET `/reputation/<user_id>` 🔒 — Get a user's reputation score and ratings

**Success response `200`**
```json
{
  "user_id": 1,
  "score": 5.0,
  "ratings": [5]
}
```

---

#### POST `/reputation/<user_id>/rate` 🔒 — Submit a rating for a user

```json
{
  "rating": 5
}
```

**Response `201`**
```json
{
  "user_id": 1,
  "score": 5.0,
  "ratings": [5]
}
```

---

#### GET `/reputation/<user_id>/badges` 🔒 — Get badges earned by a user

**Success response `200`**
```json
{
  "user_id": 1,
  "badges": ["trusted"]
}
```

`badges` is `["trusted"]` once the average score reaches 4, otherwise `["new"]`.

---

### Mentors (`/api/v1/mentors`)

#### GET `/mentors` 🔒 — List mentors

Optional query params: `?expertise=`, `?availability=`

**Success response `200`**
```json
[]
```

> There is currently no `POST /mentors` endpoint to create a mentor — the in-memory store starts empty.

---

#### GET `/mentors/<mentor_id>` 🔒 — Get a mentor by ID

**Not found `404`**
```json
{
  "error": "Mentor not found"
}
```

---

### Bookings (`/api/v1/bookings`)

#### POST `/bookings` 🔒 — Create a mentor session booking

```json
{
  "mentor_id": 1,
  "user_id": 1
}
```

**Success response `201`**
```json
{
  "id": 1,
  "mentor_id": 1,
  "user_id": 1
}
```

---

#### GET `/bookings` 🔒 — List bookings

Optional query params: `?user_id=`, `?role=`

**Success response `200`** — array of booking objects (see above).

---

#### PATCH `/bookings/<booking_id>` 🔒 — Update a booking

```json
{
  "status": "confirmed"
}
```

**Success response `200`** — full booking object with the field merged in. **Not found `404`**: `{"error": "Booking not found"}`

---

#### POST `/bookings/<booking_id>/feedback` 🔒 — Submit feedback for a completed booking

```json
{
  "rating": 5,
  "comment": "Great session"
}
```

**Response `201`**
```json
{
  "updated": true,
  "booking": {
    "id": 1,
    "mentor_id": 1,
    "user_id": 1,
    "feedback": {
      "rating": 5,
      "comment": "Great session"
    }
  }
}
```

**Not found `404`**
```json
{
  "error": "Booking not found"
}
```

---

### Deal Rooms (`/api/v1/deal-rooms`)

#### POST `/deal-rooms` 🔒 — Create a deal room

```json
{
  "startup_id": 1,
  "nda_required": true
}
```

**Success response `201`**
```json
{
  "id": 1,
  "startup_id": 1,
  "nda_required": true,
  "documents": [],
  "access_logs": []
}
```

---

#### GET `/deal-rooms/<room_id>` 🔒 — Get a deal room

**Success response `200`** — same shape as create. **Not found `404`**: `{"error": "Deal room not found"}`

---

#### POST `/deal-rooms/<room_id>/nda/sign` 🔒 — Sign the NDA for a deal room

No request body needed.

**Success response `200`**
```json
{
  "room_id": 1,
  "nda_signed": true
}
```

---

#### POST `/deal-rooms/<room_id>/documents` 🔒 — Add a document

```json
{
  "name": "deck.pdf",
  "url": "https://storage.local/deck.pdf"
}
```

**Success response `201`**
```json
{
  "id": 1,
  "name": "deck.pdf",
  "url": "https://storage.local/deck.pdf"
}
```

---

#### GET `/deal-rooms/<room_id>/documents/<doc_id>/download` 🔒 — Get a document's download URL

No request body needed. Logs a `download` event to the room's access log.

**Success response `200`**
```json
{
  "download_url": "https://storage.local/deck.pdf"
}
```

**Document not found `404`**
```json
{
  "error": "Document not found"
}
```

---

#### GET `/deal-rooms/<room_id>/access-logs` 🔒 — Get the deal room's access log

**Success response `200`**
```json
[
  {
    "event": "download",
    "doc_id": 1
  }
]
```

---

### Messages (`/api/v1/messages`)

#### POST `/messages` 🔒 — Send a message

```json
{
  "to": 2,
  "from": 1,
  "body": "hi"
}
```

**Success response `201`**
```json
{
  "id": 1,
  "to": 2,
  "from": 1,
  "body": "hi"
}
```

---

#### GET `/messages` 🔒 — List messages

Optional query params: `?thread_with=`, `?deal_room_id=`

**Success response `200`** — array of message objects (see above).

---

### Notifications (`/api/v1/notifications`)

#### GET `/notifications` 🔒 — List notifications for the current user

Filtered server-side by the caller's JWT identity.

**Success response `200`**
```json
[]
```

> Nothing currently calls `send_notification()` from a route, so this list will stay empty until a notification-producing flow is wired up.

---

#### PATCH `/notifications/<notification_id>/read` 🔒 — Mark a notification as read

No request body needed.

**Success response `200`**
```json
{
  "id": 1,
  "user_id": 1,
  "message": "...",
  "read": true
}
```

**Not found `404`**
```json
{
  "error": "Notification not found"
}
```

---

### Voice (`/api/v1/voice`)

#### POST `/voice/navigate` 🔒 — Voice-driven navigation intent (stub)

```json
{
  "intent": "go_home"
}
```

**Response `200`**
```json
{
  "intent": "go_home",
  "status": "stub"
}
```

---

#### POST `/voice/pitch-submission` 🔒 — Submit a pitch via voice transcript (stub)

```json
{
  "transcript": "hello"
}
```

**Response `202`**
```json
{
  "transcript": "hello",
  "status": "queued"
}
```

---

### Admin (`/api/v1/admin`)

All endpoints below require a JWT whose `role` claim is `admin` (set at registration). Non-admin callers get:

```json
{
  "error": "Forbidden"
}
```
`403`

#### GET `/admin/verifications/pending` 🔒admin — List pending user verifications

**Success response `200`**
```json
[]
```

---

#### POST `/admin/verifications/<user_id>/approve` 🔒admin — Approve a user's verification

No request body needed.

**Success response `200`**
```json
{
  "approved": true,
  "user_id": 2
}
```

---

#### GET `/admin/audit-logs` 🔒admin — Get the admin audit log

**Success response `200`**
```json
[
  {
    "event": "verification_approved",
    "user_id": 2
  }
]
```

---

#### POST `/admin/moderation/<content_id>/flag` 🔒admin — Flag content for moderation

No request body needed.

**Success response `200`**
```json
{
  "flagged": true,
  "content_id": 5
}
```

## Project structure

```
app/
├── __init__.py          # App factory, blueprint registration
├── config.py            # Flask config from environment variables
├── extensions.py        # Shared extension instances (bcrypt, jwt, cors)
├── models/               # Data model definitions
├── routes/               # Blueprints, one per resource
└── services/              # Business logic (auth, matching, AI evaluation, notifications, etc.)
run.py                    # Entrypoint
Procfile                  # gunicorn start command for deployment
```
