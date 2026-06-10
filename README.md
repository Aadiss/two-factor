# Two-Factor Authentication App

A simple 2FA application with username/password login and support for:
- **TOTP** (Authenticator apps like Microsoft Authenticator, Google Authenticator)
- **Passkeys** (Hardware security keys like YubiKey)

## Prerequisites

- Python 3.12+
- Node.js 18+
- MongoDB (running on localhost:27017)

## Quick Start

### 1. Start MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7

# Or use a local MongoDB installation
mongod
```

### 2. Start Backend

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Open Browser

Visit http://localhost:5173

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
└── docker-compose.yml # MongoDB container
```
