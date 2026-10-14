# CampusCircle

CampusCircle is a mobile-first student community savings and peer-to-peer lending MVP for university communities in Nigeria.

## Run locally

```bash
npm install
npm run dev
```

Start the API and PostgreSQL in separate terminals:

```bash
cp .env.example .env
docker compose up -d postgres
cd backend && python3.12 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The production build and focused unit test are available with:

```bash
npm run build
npm test
```

## Current MVP scope

The Vite/React client includes:

- Dashboard with savings, contribution, available-balance, activity and progress views.
- Circle discovery, fictional demo circles, create-circle modal and join interaction.
- Authenticated-looking profile with university/email verification and explicit simulated BMONI onboarding status.
- Circle chat with message history, sending, empty/error-safe voice-note affordance and responsive mobile layout.
- CampusCircle Copilot panel using a deterministic local fallback. Responses are labelled `SIMULATED`.
- Explicit demo-mode banner so fictional figures cannot be mistaken for real balances or payments.

The API now provides PostgreSQL-backed registration, hashed expiring email OTP verification, circles, membership-checked chat writes, and isolated Brevo/Groq/BMONI adapters. Financial provider actions fail closed when BMONI credentials or documented permissions are unavailable. The environment template keeps server-only credentials out of frontend code:

```bash
cp .env.example .env
```

The remaining production work is deliberately not represented as fake success: migrations, full session refresh/revocation, ledger posting, proposal/version voting routes, and BMONI capability-specific endpoints must be completed against the provider's current permissions and documentation before enabling money movement.