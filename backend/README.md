# Backend - AI Irrigation Scheduler

Django REST Framework backend with JWT authentication.

## Setup Instructions

### 1. Create Virtual Environment

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Variables

Copy `.env.example` to `.env` and update values:

```powershell
copy .env.example .env
```

Generate a secure secret key:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Database Setup

Make sure PostgreSQL is running (or use Docker Compose from root).

Run migrations:
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```powershell
python manage.py createsuperuser
```

### 6. Run Development Server

```powershell
python manage.py runserver
```

Backend will be available at: `http://localhost:8000`

## API Endpoints

### Authentication

- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/user/` - Get current user details
- `PUT /api/auth/user/` - Update user profile
- `POST /api/auth/change-password/` - Change password

## Testing

Run tests with pytest:

```powershell
pytest
```

Run with coverage:

```powershell
pytest --cov=apps
```

## Project Structure

```
backend/
├── config/                 # Django settings & URLs
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   └── authentication/     # User authentication app
│       ├── models.py       # Custom User model
│       ├── serializers.py  # DRF serializers
│       ├── views.py        # API views
│       ├── urls.py         # URL routing
│       └── tests.py        # Unit tests
├── requirements.txt        # Python dependencies
├── manage.py              # Django management script
└── .env.example           # Environment variables template
```

## Next Steps

- Phase 2: Fields & Crops management
- Phase 3: Weather API integration
- Phase 4: AI model integration
