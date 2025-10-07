# Smart Irrigation Frontend

This is the Next.js frontend application for the Smart Irrigation Scheduling system.

## Features

- User authentication (register, login, logout)
- JWT token management with automatic refresh
- Protected routes with auth guards
- Profile management
- Responsive UI with Tailwind CSS
- TypeScript for type safety

## Tech Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **State Management**: React Context API
- **Cookie Management**: js-cookie

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running at `http://localhost:8000`

### Installation

1. Install dependencies:
```powershell
cd frontend
npm install
```

2. Create environment file:
```powershell
cp .env.example .env
```

3. Update `.env` with your API URL (default is localhost:8000):
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Development

Start the development server:
```powershell
npm run dev
```

The application will be available at `http://localhost:3000`

### Build

Build for production:
```powershell
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── pages/           # Next.js pages
│   │   ├── _app.tsx     # App wrapper with AuthProvider
│   │   ├── index.tsx    # Home page (redirects)
│   │   ├── login.tsx    # Login page
│   │   ├── register.tsx # Registration page
│   │   ├── dashboard.tsx # Main dashboard
│   │   └── profile.tsx  # User profile
│   ├── components/
│   │   └── auth/
│   │       └── AuthGuard.tsx # Protected route wrapper
│   ├── contexts/
│   │   └── AuthContext.tsx # Auth state management
│   ├── lib/
│   │   └── api.ts       # Axios instance with interceptors
│   ├── types/
│   │   └── auth.ts      # TypeScript types
│   └── styles/
│       └── globals.css  # Global styles + Tailwind
├── public/              # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Available Pages

- `/` - Home (redirects to dashboard or login)
- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Main dashboard (protected)
- `/profile` - User profile management (protected)

## API Integration

The frontend connects to the Django backend API with:

- **Base URL**: `NEXT_PUBLIC_API_URL` environment variable
- **Authentication**: JWT tokens stored in cookies
- **Endpoints**:
  - `POST /auth/register/` - User registration
  - `POST /auth/login/` - User login (returns JWT tokens)
  - `POST /auth/refresh/` - Refresh access token
  - `GET /auth/user/` - Get current user
  - `PATCH /auth/user/` - Update user profile
  - `PUT /auth/change-password/` - Change password

## Authentication Flow

1. User registers or logs in
2. JWT tokens (access & refresh) stored in cookies
3. Access token automatically added to all API requests
4. On 401 error, refresh token used to get new access token
5. If refresh fails, user redirected to login

## Notes

- TypeScript errors in the editor are expected until `npm install` is run
- The auth system is production-ready with token refresh logic
- All protected pages wrapped in `AuthGuard` component
- Farmer-friendly UI with emojis and simple language

## Next Steps (Phase 2+)

- Field management pages
- Weather integration
- AI-powered irrigation scheduling
- History and analytics
- Settings page
