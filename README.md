# Two-Factor Authentication App

A simple 2FA application with username/password login and support for:
- **TOTP** (Authenticator apps like Microsoft Authenticator, Google Authenticator)
- **Passkeys** (Hardware security keys like YubiKey)

## Prerequisites

- Docker and Docker Compose

## Quick Start

### 1. Run the Application

```bash
docker compose up --build
```

This will start all services:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **MongoDB**: localhost:27017

### 2. Open Browser

Visit http://localhost:3000

## Usage

1. **Register** a new account
2. **Login** with your credentials
3. Go to **Dashboard** and set up 2FA:
   - Click "Setup Authenticator App" to scan QR code with Microsoft/Google Authenticator
   - Click "Setup Security Keys" to register a YubiKey or other hardware key
4. **Logout** and login again - you'll be prompted for your 2FA code

## API Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user
- `POST /api/2fa/totp/setup` - Setup TOTP
- `POST /api/2fa/totp/verify` - Verify TOTP setup
- `POST /api/2fa/totp/validate` - Validate TOTP code
- `POST /api/2fa/passkey/register/begin` - Start passkey registration
- `POST /api/2fa/passkey/register/complete` - Complete passkey registration
- `GET /api/2fa/passkey/list` - List registered passkeys
- `DELETE /api/2fa/passkey/:id` - Remove passkey

## Project Structure

```
two-factor/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py        # Entry point
│   │   ├── config.py      # Configuration
│   │   ├── database.py    # MongoDB connection
│   │   ├── models/        # Pydantic models
│   │   ├── routes/        # API routes
│   │   └── services/      # Business logic
│   └── requirements.txt
├── frontend/          # Vue 3 frontend
│   ├── src/
│   │   ├── views/         # Vue components
│   │   ├── stores/        # Pinia stores
│   │   └── api/           # Axios config
│   └── package.json
└── docker-compose.yml # Service orchestration
```