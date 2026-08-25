# OrthofinixAI — STAR Summit Edition

AI-powered orthodontic finishing assessment platform with **Android app**, **React web app**, and **FastAPI cloud backend**.

## Project Structure

```
OrthofinixAi/
├── app/                 # Android (Kotlin + Jetpack Compose)
├── backend/             # FastAPI + clinical AI engine
├── web/                 # React + Vite + TypeScript + Tailwind
├── docker-compose.yml
└── README.md
```

## Quick Start — Live Demo (STAR Summit)

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Web App
```bash
cd web
cp .env.example .env
npm install
npm run dev
```
Open http://localhost:5173 → **Try Demo** on login or dashboard.

### 3. Android APK
```bash
gradlew.bat assembleDebug
```
APK: `app/build/outputs/apk/debug/app-debug.apk`

## API Endpoints (Summit)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | JWT login |
| POST | `/analysis/upload` | Upload image |
| POST | `/analysis/analyze` | Run AI (form: `demo=true` for instant demo) |
| GET | `/analysis/history` | User report list |
| GET | `/analysis/report/{id}` | Full report |

Legacy Android routes remain under `/api/*`.

## Environment Variables

**Backend** (`backend/.env`):
```
JWT_SECRET_KEY=your-secret
DATABASE_URL=sqlite:///./orthofinix_summit.db
PORT=8000
```

**Web** (`web/.env`):
```
VITE_API_URL=http://127.0.0.1:8000
```

## Cloud Deployment

### Web → Vercel
1. Import `web/` folder to Vercel
2. Set `VITE_API_URL` to your Render backend URL
3. Build: `npm run build`

### Backend → Render
1. Connect `backend/` repo
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set `JWT_SECRET_KEY` in Render env

### Docker (full stack)
```bash
docker-compose up --build
```

## Demo Mode

- **Web**: Login → "Try Demo" or Upload → "Try Demo"
- **Android**: Dashboard → "Try Demo" (empty state) or loads instant clinical report
- **Backend**: `POST /analysis/analyze` with `demo=true`

Works offline on Android (on-device AI). Web falls back to cached demo report if backend is down.

## Clinical Features

- Andrews' Six Keys evaluation
- Overjet / overbite (mm, %)
- Molar classification (Class I/II/III)
- FDI tooth-specific findings
- Root uprighting analysis
- Confidence scoring & low-confidence warnings

## Test Account

Register at `/register` or use demo mode without backend.

---

**OrthofinixAI** — Finish. Verified. Perfected.
