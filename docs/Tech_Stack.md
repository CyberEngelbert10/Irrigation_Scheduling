# Project Tech Stack

This document records the agreed technical stack for the AI-Based Crop Irrigation Scheduler and recommended libraries/tools for development, testing, and deployment.

## Core stack
- Frontend: Next.js (TypeScript)
- Backend: Django (Django REST Framework)
- Styling: Tailwind CSS
- Database: PostgreSQL
- ML model: scikit-learn (existing `rf_irrigation_model.pkl`)

## Recommended backend libraries
- `djangorestframework` — JSON API support
- `psycopg2-binary` — PostgreSQL driver
- `django-cors-headers` — enable CORS for local dev and cross-origin requests
- `django-environ` or `python-dotenv` — manage environment variables
- `djangorestframework-simplejwt` — JWT authentication (optional)
- `celery` + `redis` — background jobs and scheduled tasks (optional)
- `gunicorn` or `uvicorn` — production application server
- `whitenoise` — serve static files when deploying Django alone

## Recommended frontend libraries
- `swr` or `react-query` — client-side data fetching and caching
- `axios` — HTTP client (optional)
- `react-hook-form` + `zod` or `yup` — forms + validation
- `leaflet` or `mapbox-gl` — interactive maps for fields (optional)

## Testing & quality
- Frontend: Jest + React Testing Library, Cypress (E2E)
- Backend: pytest, pytest-django, factory-boy
- Linters/formatters: ESLint + Prettier (frontend), Black + isort + Flake8 (backend)
- Type checking: TypeScript (frontend), mypy (backend)

## Dev / Ops
- Docker & docker-compose — local dev and reproducible environments
- GitHub Actions — CI for tests/lint/builds
- Sentry — error monitoring (optional)
- Redis — cache & Celery broker

## ML / Model operations
- `scikit-learn`, `pandas`, `numpy`, `joblib` — load and run the existing model, preprocess inputs
- Optionally: MLflow or a small model-serving microservice (FastAPI) for versioning and A/B testing

## Minimal install snippets (PowerShell)

### Backend (virtual environment)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install django djangorestframework psycopg2-binary django-cors-headers python-dotenv scikit-learn joblib pandas numpy
```

Optional backend extras:
```powershell
pip install djangorestframework-simplejwt celery redis whitenoise django-environ
```

### Frontend (Next.js + Tailwind)
```powershell
npx create-next-app@latest frontend --typescript
cd frontend
npm install tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install swr axios react-hook-form zod
```

### Docker (recommended)
- Create a `Dockerfile` for Django and Next.js and a `docker-compose.yml` that includes Postgres and Redis.

## Next steps you can pick (I can implement any):
- Add a `docker-compose` setup for Django + Next.js + Postgres + Redis.
- Scaffold Django project with DRF and a single prediction endpoint that loads `rf_irrigation_model.pkl`.
- Scaffold Next.js project with Tailwind and a page that calls the prediction API.
- Add CI (GitHub Actions) with tests and linting.

If you want, I will add the first option (Docker compose skeleton) now.
