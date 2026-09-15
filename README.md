# 📄 README profesional en inglés

**Abre `README.md` en VS Code, borra todo y pega esto:**

---

```markdown
# 🦷 Rehab Oral y Estética

> Real-time patient communication platform built with Django Channels and WebSockets for a dental clinic in Querétaro, Mexico.

[![Tests](https://github.com/JulsMonjaraz/rehab-oral-estetica/actions/workflows/tests.yml/badge.svg)](https://github.com/JulsMonjaraz/rehab-oral-estetica/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)](https://github.com/JulsMonjaraz/rehab-oral-estetica)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1-092E20?style=flat&logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-REST-ff1709?style=flat&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Channels](https://img.shields.io/badge/Channels-WebSockets-blue)](https://channels.readthedocs.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5-37814A?style=flat&logo=celery)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📖 Overview

**Rehab Oral y Estética** is a real-time communication platform that lets dental patients chat directly with the clinic's staff (receptionists and doctors) through a modern web interface.

The system replaces a chaotic WhatsApp-based workflow with a proper ticketing and chat platform, with role-based access control, real-time notifications, and automated weekly reports.

The API is documented with Swagger/ReDoc and the entire codebase is covered by 38 tests with **93% test coverage**.

## 🏥 About the client

**Rehab Oral y Estética** is a dental clinic in Querétaro, Mexico, specialized in oral rehabilitation and aesthetic dentistry (implants, prosthetics, and smile design).

The clinic handles a high volume of patient inquiries daily and needed a professional tool to manage them without losing track of any conversation.

## 🎯 The challenge

Before this project, the clinic managed patient communication manually:

- **WhatsApp chaos:** Patient messages got lost between personal chats.
- **No visibility:** No way to see which patients were waiting for a response.
- **Mixed priorities:** Dental emergencies (acute pain) were mixed with routine questions.
- **No history:** No record of past conversations with each patient.
- **No metrics:** No way to measure response times or staff performance.

The clinic needed a structured tool that professionalized patient communication while keeping the human touch.

## 💡 The solution

I designed and built a **real-time communication platform** that digitalizes the entire patient inquiry workflow, from the moment a patient opens a conversation to the moment their case is closed.

### For patients

- Register and login (JWT authentication).
- Create a new inquiry with a reason and description.
- **Chat in real time** with the clinic staff.
- See the full history of their past inquiries.
- Mark inquiries as urgent (for dental emergencies).

### For receptionists

- Dashboard with ALL open inquiries.
- **See messages arriving in real time** (WebSockets).
- Assign inquiries to doctors by specialty.
- Respond directly to patients.
- **Live notifications** when a new inquiry or message arrives.

### For doctors

- See only inquiries assigned to them.
- Chat with patients in real time.
- Close inquiries when the case is resolved.
- Receive only relevant notifications (assigned cases).

### For admins

- Everything above plus:
- **Automated weekly reports** by email with metrics.
- Full visibility of all inquiries and users.
- User management with role assignment.

## ✨ Features

### Real-Time Communication
- **WebSocket chat** for each inquiry using Django Channels.
- **Live notifications** for the staff when a new inquiry or message arrives.
- **JWT authentication over WebSockets** via custom middleware.
- **Role-based access control** inside each consumer.

### REST API
- **Full CRUD** for inquiries and messages.
- **Custom endpoints** for assigning inquiries to doctors and closing them.
- **Multi-role permissions:** patients see their own inquiries, doctors see only assigned ones, staff sees everything.
- **JWT authentication** with access and refresh tokens.

### Async & Background Jobs
- **Celery + Redis** for background task processing.
- **Weekly automated reports** sent every Monday at 9 AM to all admins.
- **Celery Beat** for scheduled tasks.
- Report includes: new inquiries, closed inquiries, urgent cases, messages exchanged, staff activity.

### DevOps
- **Docker Compose** with 5 services: `web`, `db`, `redis`, `worker`, `beat`.
- **CI/CD with GitHub Actions** — 38 tests run on every push.
- **93% test coverage** including WebSocket tests with `WebsocketCommunicator`.

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Framework | Django 6.1 |
| Real-time | Django Channels 4 + WebSockets |
| ASGI Server | Daphne |
| API | Django REST Framework |
| Auth | JWT (SimpleJWT) |
| Database | PostgreSQL 15 |
| Cache & Broker | Redis 7 |
| Async Tasks | Celery 5 + Celery Beat |
| Testing | pytest, pytest-django, pytest-asyncio, factory-boy |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────┐
│  Browser (Patient / Receptionist / Doctor / Admin)    │
│  ├── HTTP + JWT                                       │
│  └── WebSocket + JWT                                  │
└────────────────────┬──────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐        ┌─────────────────┐
│  Django       │        │  Django Channels│
│  DRF (REST)   │        │  (WebSockets)   │
│  Daphne ASGI  │        │  Async Consumers│
└───────┬───────┘        └────────┬────────┘
        │                         │
        └────────────┬────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
  ┌───────────┐            ┌───────────┐
  │ PostgreSQL│            │  Redis    │
  └───────────┘            │  (pub/sub)│
                           └─────┬─────┘
                                 │
                          ┌──────┴────────┐
                          ▼               ▼
                   ┌───────────┐   ┌────────────┐
                   │  Worker   │   │    Beat    │
                   │  (Celery) │   │  (Celery)  │
                   └───────────┘   └────────────┘
```

## 📡 WebSocket Endpoints

| URL | Description | Auth |
|-----|-------------|------|
| `ws://localhost:8000/ws/chat/<inquiry_id>/?token=<jwt>` | Real-time chat for a specific inquiry | JWT |
| `ws://localhost:8000/ws/notificaciones/?token=<jwt>` | Global notifications for staff | JWT (staff only) |

**Access control:**
- Patients can only connect to their own inquiries.
- Doctors can only connect to inquiries assigned to them.
- Receptionists and admins can connect to any inquiry.
- Only staff (not patients) can connect to the notifications consumer.

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/token/` | Obtain JWT access + refresh tokens |
| `POST` | `/api/token/refresh/` | Refresh access token |
| `GET` | `/api/users/me/` | Get current authenticated user |
| `GET/POST` | `/api/consultas/` | List / create inquiries (filtered by role) |
| `POST` | `/api/consultas/{id}/asignar/` | Assign a doctor to an inquiry (staff only) |
| `POST` | `/api/consultas/{id}/cerrar/` | Close an inquiry (staff only) |
| `GET/POST` | `/api/mensajes/` | List / create messages |

## 🧪 Testing

Run the full test suite:

```bash
pytest
```

With coverage report:

```bash
pytest --cov=consultas --cov-report=term-missing
```

**Current coverage: 93%** across 38 tests covering:
- Models (roles, multi-tenancy logic).
- API endpoints and permission rules.
- WebSocket consumers (`ChatConsumer` and `NotificacionesConsumer`).
- Celery tasks (weekly report generation).

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose

### 1. Clone the repository
```bash
git clone https://github.com/JulsMonjaraz/rehab-oral-estetica.git
cd rehab-oral-estetica
```

### 2. Create the environment file
```bash
cp .env.example .env
# Edit .env if needed
```

### 3. Build and start all services
```bash
docker compose up --build
```

The API will be available at `http://127.0.0.1:8000`.

### 4. Run migrations and create a superuser
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## 📁 Project Structure

```
rehab-oral-estetica/
├── .github/
│   └── workflows/
│       └── tests.yml                 # CI/CD pipeline
├── config/
│   ├── celery.py                     # Celery configuration
│   ├── asgi.py                       # ASGI + WebSocket routing
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── consultas/
│   ├── migrations/
│   ├── templates/consultas/
│   │   ├── chat_test.html            # WebSocket chat demo
│   │   └── notificaciones_test.html  # WebSocket notifications demo
│   ├── tests/
│   │   ├── factories.py
│   │   ├── test_api.py
│   │   ├── test_models.py
│   │   ├── test_tasks.py
│   │   └── test_websockets.py
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py                  # WebSocket consumers
│   ├── middleware.py                 # JWT middleware for WebSockets
│   ├── models.py                     # User, Consulta, Mensaje
│   ├── permissions.py                # Role-based permissions
│   ├── routing.py                    # WebSocket URL routing
│   ├── serializers.py
│   ├── signals.py                    # Auto-trigger notifications
│   ├── tasks.py                      # Celery tasks
│   ├── urls.py
│   └── views.py
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Debug mode (True/False) |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL user |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port |
| `REDIS_URL` | Redis URL for cache and WebSockets |
| `CELERY_BROKER_URL` | Celery broker URL |
| `CELERY_RESULT_BACKEND` | Celery result backend URL |

## 👨‍💻 Author

**Julio Monjaraz**  
Backend developer specialized in Django and Python.

- [GitHub](https://github.com/JulsMonjaraz)
- [LinkedIn](https://www.linkedin.com/in/juliomonjaraz/)

Built for [Rehab Oral y Estética](https://www.facebook.com/rehaboralyestetica) in Querétaro.

---
