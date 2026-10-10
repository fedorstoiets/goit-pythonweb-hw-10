# goit-pythonweb-hw-10

Homework #10 for **GoIT FullStack Web Development with Python**.

**Author:** Fedor Stoietskyi

This project extends the contacts REST API with authentication, JWT authorization, user-owned contacts, email verification, rate limiting, CORS, and Cloudinary avatar uploads.

## Scoring coverage

| Requirement                 | Implementation                                |
| --------------------------- | --------------------------------------------- |
| Authentication — 20 pts     | Registration, password hashing, login         |
| JWT authorization — 20 pts  | Bearer `access_token`                         |
| Own contacts only — 10 pts  | Every contact query is filtered by `owner_id` |
| Email verification — 20 pts | Signed verification token + Mailpit SMTP      |
| `/me` rate limit — 10 pts   | 5 requests/minute using SlowAPI               |
| CORS — 5 pts                | FastAPI `CORSMiddleware`                      |
| Cloudinary avatar — 15 pts  | Authenticated avatar upload endpoint          |

## Important HTTP behavior

- duplicate registration email → `409 Conflict`;
- passwords are hashed with bcrypt;
- successful registration → `201 Created`;
- contact creation → `201 Created`;
- incorrect email/password → `401 Unauthorized`;
- protected endpoints require a JWT access token;
- users can only read/update/delete their own contacts.

## Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Alembic
- Pydantic v2
- PyJWT
- Passlib + bcrypt
- SlowAPI
- Cloudinary
- Mailpit
- Docker Compose

## Project structure

```text
goit-pythonweb-hw-10/
├── app/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── contacts.py
│   │   └── users.py
│   ├── services/
│   │   ├── cloudinary_service.py
│   │   └── email.py
│   ├── config.py
│   ├── crud.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── security.py
├── alembic/
├── Dockerfile
├── docker-compose.yaml
├── seed.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Environment

Copy the sample environment file:

```powershell
Copy-Item .env.example .env
```

Generate a strong JWT secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Paste the generated value into:

```text
JWT_SECRET_KEY=...
```

Do not commit `.env`.

For Cloudinary avatar upload, add your real Cloudinary values:

```text
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

## Docker Compose

All application services are launched with Docker Compose:

- FastAPI app;
- PostgreSQL;
- Mailpit SMTP/testing UI.

Start:

```powershell
docker compose up -d --build
```

Check:

```powershell
docker compose ps
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Mailpit:

```text
http://127.0.0.1:8025
```

## Registration and email verification

Register:

```http
POST /api/auth/register
```

Example:

```json
{
  "username": "Fedor",
  "email": "fedor@example.com",
  "password": "StrongPassword123!"
}
```

Successful registration returns `201 Created`.

The verification email is sent to Mailpit in the local Docker environment.

Open:

```text
http://127.0.0.1:8025
```

Open the email and click/copy the verification URL.

Verification endpoint:

```http
GET /api/auth/verify-email?token=...
```

Resend verification:

```http
POST /api/auth/resend-verification?email=fedor@example.com
```

## Login / JWT

Login accepts JSON in the request body:

```http
POST /api/auth/login
```

```json
{
  "email": "fedor@example.com",
  "password": "StrongPassword123!"
}
```

Successful response:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

In Swagger click **Authorize** and paste the access token.

## Protected contacts

All contacts endpoints require authorization.

| Method | Endpoint                           |
| ------ | ---------------------------------- |
| POST   | `/api/contacts`                    |
| GET    | `/api/contacts`                    |
| GET    | `/api/contacts/search`             |
| GET    | `/api/contacts/upcoming-birthdays` |
| GET    | `/api/contacts/{contact_id}`       |
| PUT    | `/api/contacts/{contact_id}`       |
| DELETE | `/api/contacts/{contact_id}`       |

Every query includes the authenticated user's `owner_id`. A user therefore cannot access another user's contacts.

## Current user and rate limiting

```http
GET /api/users/me
```

The route is limited to:

```text
5 requests per minute per client IP
```

Additional requests receive HTTP `429 Too Many Requests`.

## Avatar upload

Authenticated route:

```http
PATCH /api/users/avatar
```

Upload an image with multipart/form-data using field:

```text
file
```

The image is uploaded to Cloudinary and its secure URL is stored in the user's database record.

Real Cloudinary credentials must be configured in `.env`.

## CORS

CORS is enabled through FastAPI `CORSMiddleware`.

Allowed origins are configured with:

```text
CORS_ORIGINS=...
```

## Database migrations

The app container automatically runs:

```text
alembic upgrade head
```

before starting FastAPI.

Manual check:

```powershell
docker compose exec app alembic current
```

## Optional demo data

Run:

```powershell
docker compose exec app python seed.py
```

Demo credentials:

```text
email: demo@example.com
password: DemoPassword123!
```

The demo user is already verified.
