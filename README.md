# Portafolio API

REST API backend built with **FastAPI** designed to power developer portfolio sites. It manages user profiles, social contacts, programming languages, tech stack, and projects — all with image upload support via Supabase Storage.

Built as a real-world backend ready to be consumed by any frontend (Next.js, React, Vue, etc.) or mobile app.

**Stack:** Python · FastAPI · PostgreSQL · SQLAlchemy 2.0 · Pydantic v2 · JWT Auth · Supabase Storage · Alembic · Docker

---

## Table of Contents

- [Live Docs](#live-docs)
- [Features](#features)
- [Authentication](#authentication)
- [API Reference](#api-reference)
  - [Auth](#auth)
  - [Users](#users)
  - [Contacts](#contacts)
  - [Languages](#languages)
  - [Stack](#stack)
  - [Projects](#projects)
- [Integration Guide](#integration-guide)
- [Running Locally](#running-locally)
- [Docker Deployment](#docker-deployment)
- [Environment Variables](#environment-variables)

---

## Live Docs

Once running, the interactive Swagger UI is available at:

```
http://localhost:8000/docs
```

ReDoc alternative:

```
http://localhost:8000/redoc
```

---

## Features

- JWT-based authentication with role system (`admin` / `user`)
- Full CRUD for users, contacts, projects, languages, and tech stack
- File upload for user avatars, contact images, and project screenshots via Supabase Storage
- Soft deletes (status boolean) — data is never hard-deleted
- Pagination on all list endpoints (`skip` / `limit`)
- Layered architecture: Router → Service → ORM — easy to extend

---

## Authentication

The API uses **OAuth2 with Bearer tokens (JWT)**.

### Get a token

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

**Response:**

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}
```

### Use the token

Include the token in the `Authorization` header on protected endpoints:

```
Authorization: Bearer <jwt_token>
```

### Role system

| Role    | Capabilities                                              |
|---------|-----------------------------------------------------------|
| `user`  | Manage their own profile, contacts, projects, languages, stack |
| `admin` | All of the above + manage any user + manage catalog data (languages/stacks) |

---

## API Reference

All endpoints are prefixed relative to the base URL (e.g., `https://api.yourdomain.com`).

Paginated list endpoints accept `?skip=0&limit=10` query parameters.

---

### Auth

| Method | Endpoint        | Auth | Description                  |
|--------|-----------------|------|------------------------------|
| POST   | `/auth/register` | No  | Register a new user          |
| POST   | `/auth/login`    | No  | Login and receive JWT token  |

#### Register

```http
POST /auth/register
Content-Type: application/json

{
  "name": "John",
  "last_name1": "Doe",
  "last_name2": "Smith",
  "email": "john@example.com",
  "phone_number": "+1234567890",
  "password": "securepassword",
  "title": "Full Stack Developer"
}
```

---

### Users

| Method | Endpoint                    | Auth        | Description                         |
|--------|-----------------------------|-------------|-------------------------------------|
| GET    | `/users`                    | No          | List users (filterable)             |
| GET    | `/users/{user_id}`          | No          | Get user by ID                      |
| PATCH  | `/users/{user_id}`          | Own / Admin | Update profile fields               |
| PATCH  | `/users/{user_id}/email`    | Own / Admin | Change email and/or password        |
| PATCH  | `/users/{user_id}/image`    | Own / Admin | Upload profile picture              |
| PATCH  | `/users/{user_id}/rol`      | Admin       | Change user role                    |
| PATCH  | `/users/{user_id}/status`   | Admin       | Toggle user active/inactive         |

#### List users — query params

| Param    | Type    | Description             |
|----------|---------|-------------------------|
| `name`   | string  | Filter by name          |
| `email`  | string  | Filter by email         |
| `rol`    | string  | `admin` or `user`       |
| `status` | boolean | Active (`true`) or not  |
| `skip`   | int     | Pagination offset       |
| `limit`  | int     | Pagination page size    |

#### Update profile

```http
PATCH /users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Jane",
  "title": "Backend Engineer",
  "description": "I build scalable APIs."
}
```

#### Upload profile image

```http
PATCH /users/{user_id}/image
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image file>
```

---

### Contacts

Contacts represent social links or media profiles (GitHub, LinkedIn, etc.) belonging to a user. Each contact can optionally have an image/icon.

| Method | Endpoint                               | Auth        | Description                      |
|--------|----------------------------------------|-------------|----------------------------------|
| POST   | `/Contact/{user_id}`                   | Own / Admin | Create a contact                 |
| GET    | `/Contact/{user_id}/user`              | No          | List contacts for a user         |
| GET    | `/Contact/{contact_id}`                | No          | Get a contact by ID              |
| PATCH  | `/Contact/{contact_id}`                | Own / Admin | Update contact fields            |
| PATCH  | `/Contact/{contact_id}/{user_id}/image`| Own / Admin | Upload contact image             |
| PATCH  | `/Contact/{contact_id}/status`         | Own / Admin | Toggle contact active/inactive   |

#### Create a contact

```http
POST /Contact/{user_id}
Authorization: Bearer <token>
Content-Type: multipart/form-data

name: GitHub
link: https://github.com/johndoe
file: <optional icon image>
```

**Response:**

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "GitHub",
  "link": "https://github.com/johndoe",
  "image": "https://storage.supabase.co/.../icon.png",
  "status": true
}
```

---

### Languages

The language catalog is managed by admins. Users then link themselves to languages with a proficiency level.

#### Catalog (Admin)

| Method | Endpoint                       | Auth  | Description                      |
|--------|--------------------------------|-------|----------------------------------|
| POST   | `/language`                    | Admin | Add a language to the catalog    |
| GET    | `/language`                    | No    | List catalog languages           |
| GET    | `/language/{language_id}`      | No    | Get a language by ID             |
| PATCH  | `/language/{language_id}`      | Admin | Update language name             |
| PATCH  | `/language/{language_id}/status` | Admin | Toggle language active/inactive |

#### User-Language links

| Method | Endpoint                                         | Auth        | Description                            |
|--------|--------------------------------------------------|-------------|----------------------------------------|
| POST   | `/language/user`                                 | Own / Admin | Link user to a language with a level   |
| GET    | `/language/user/{user_id}`                       | No          | List all languages for a user          |
| GET    | `/language/user/{user_id}/{language_id}`         | No          | Get a specific user-language           |
| PATCH  | `/language/user/{user_id}/{language_id}`         | Own / Admin | Update proficiency level               |
| PATCH  | `/language/user/{user_id}/{language_id}/status`  | Own / Admin | Toggle user-language active/inactive   |

#### Link a user to a language

```http
POST /language/user
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "uuid",
  "language_id": "uuid",
  "level": "Advanced"
}
```

**Response:**

```json
{
  "user_id": "uuid",
  "language_id": "uuid",
  "language_name": "Python",
  "level": "Advanced",
  "status": true
}
```

---

### Stack

Tech stack catalog (frameworks, tools, technologies). Same pattern as Languages.

#### Catalog (Admin)

| Method | Endpoint                     | Auth  | Description                   |
|--------|------------------------------|-------|-------------------------------|
| POST   | `/stack`                     | Admin | Add a technology to catalog   |
| GET    | `/stack`                     | No    | List catalog technologies     |
| GET    | `/stack/{stack_id}`          | No    | Get a technology by ID        |
| PATCH  | `/stack/{stack_id}`          | Admin | Update technology name        |
| PATCH  | `/stack/{stack_id}/status`   | Admin | Toggle active/inactive        |

#### User-Stack links

| Method | Endpoint                                      | Auth        | Description                          |
|--------|-----------------------------------------------|-------------|--------------------------------------|
| POST   | `/stack/user`                                 | Own / Admin | Link user to a technology            |
| GET    | `/stack/user/{user_id}`                       | No          | List all technologies for a user     |
| GET    | `/stack/user/{user_id}/{stack_id}`            | No          | Get a specific user-stack            |
| PATCH  | `/stack/user/{user_id}/{stack_id}/status`     | Own / Admin | Toggle user-stack active/inactive    |

#### Link a user to a technology

```http
POST /stack/user
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "uuid",
  "stack_id": "uuid"
}
```

---

### Projects

| Method | Endpoint                                  | Auth        | Description                        |
|--------|-------------------------------------------|-------------|------------------------------------|
| POST   | `/project/{user_id}`                      | Own / Admin | Create a project                   |
| GET    | `/project/{user_id}/user`                 | No          | List projects for a user           |
| GET    | `/project/{project_id}`                   | No          | Get a project by ID                |
| PATCH  | `/project/{project_id}`                   | Own / Admin | Update project fields              |
| PATCH  | `/project/{project_id}/status`            | Own / Admin | Toggle project active/inactive     |
| POST   | `/project/{project_id}/{user_id}/images`  | Own / Admin | Add images to a project            |
| DELETE | `/project/{project_id}/{user_id}/images`  | Own / Admin | Remove a specific image            |

#### Create a project

```http
POST /project/{user_id}
Authorization: Bearer <token>
Content-Type: multipart/form-data

name: My Portfolio API
description: REST API for developer portfolios
repository_link: https://github.com/user/repo
deploy_link: https://api.mydomain.com
files: <optional image files (multiple allowed)>
```

**Response:**

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "My Portfolio API",
  "description": "REST API for developer portfolios",
  "repository_link": "https://github.com/user/repo",
  "deploy_link": "https://api.mydomain.com",
  "image_link": [
    "https://storage.supabase.co/.../screenshot1.png"
  ],
  "status": true
}
```

#### Delete a project image

```http
DELETE /project/{project_id}/{user_id}/images
Authorization: Bearer <token>
Content-Type: application/json

{
  "image_url": "https://storage.supabase.co/.../screenshot1.png"
}
```

---

## Integration Guide

This section explains how to consume this API from a frontend application.

### Typical flow for a portfolio frontend

```
1. Fetch user profile        GET /users/{user_id}
2. Fetch user contacts       GET /Contact/{user_id}/user
3. Fetch user languages      GET /language/user/{user_id}
4. Fetch user stack          GET /stack/user/{user_id}
5. Fetch user projects       GET /project/{user_id}/user
```

All of these are public endpoints — no authentication required to read portfolio data.

### Example: Fetching a complete profile (JavaScript)

```javascript
const BASE_URL = 'https://api.yourdomain.com';
const USER_ID  = 'your-user-uuid-here';

async function fetchPortfolio(userId) {
  const [user, contacts, languages, stack, projects] = await Promise.all([
    fetch(`${BASE_URL}/users/${userId}`).then(r => r.json()),
    fetch(`${BASE_URL}/Contact/${userId}/user`).then(r => r.json()),
    fetch(`${BASE_URL}/language/user/${userId}`).then(r => r.json()),
    fetch(`${BASE_URL}/stack/user/${userId}`).then(r => r.json()),
    fetch(`${BASE_URL}/project/${userId}/user`).then(r => r.json()),
  ]);

  return { user, contacts, languages, stack, projects };
}
```

### Example: Authenticated request (updating profile)

```javascript
async function updateProfile(userId, token, data) {
  const res = await fetch(`${BASE_URL}/users/${userId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  return res.json();
}
```

### Example: Uploading a profile image

```javascript
async function uploadAvatar(userId, token, file) {
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${BASE_URL}/users/${userId}/image`, {
    method: 'PATCH',
    headers: { 'Authorization': `Bearer ${token}` },
    body: form,
  });
  return res.json();
}
```

### Pagination

All list endpoints support `skip` and `limit`:

```
GET /project/{user_id}/user?skip=0&limit=5
```

### Filtering

Most list endpoints accept optional query filters:

```
GET /users?rol=admin&status=true
GET /Contact/{user_id}/user?status=true
GET /language?name=python
```

---

## Running Locally

### Prerequisites

- Python 3.12+
- PostgreSQL database
- Supabase account (for file storage)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/PORTAFOLIO_API.git
cd PORTAFOLIO_API

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy the environment file and fill in your values
cp .env.example .env

# Apply database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## Docker Deployment

The project includes a multi-stage Dockerfile optimized for minimal image size. No dev dependencies are included in the final image.

### Build and run standalone

```bash
docker build -t portafolio-api .
docker run -p 8000:8000 --env-file .env portafolio-api
```

### docker-compose (recommended for VPS)

Create a `docker-compose.yml` alongside the other services on your VPS:

```yaml
services:
  portafolio-api:
    build: ./PORTAFOLIO_API
    container_name: portafolio-api
    restart: unless-stopped
    env_file: ./PORTAFOLIO_API/.env
    expose:
      - "8000"
    networks:
      - proxy

networks:
  proxy:
    external: true
```

Then point your Nginx config to `portafolio-api:8000`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass         http://portafolio-api:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
# PostgreSQL connection string
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
TOKEN_EXPIRE=24

# Supabase Storage
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-key
SUPABASE_BUCKET=PORTAFOLIO
```

| Variable        | Description                                          |
|-----------------|------------------------------------------------------|
| `DATABASE_URL`  | PostgreSQL connection string (psycopg2 driver)       |
| `SECRET_KEY`    | Secret used to sign JWT tokens                       |
| `ALGORITHM`     | JWT algorithm — use `HS256`                          |
| `TOKEN_EXPIRE`  | Token lifetime in hours                              |
| `SUPABASE_URL`  | Your Supabase project URL                            |
| `SUPABASE_KEY`  | Supabase service role key (for storage write access) |
| `SUPABASE_BUCKET` | Supabase storage bucket name                       |
