# Proyecto Final – Catálogo de Productos (MVP, tabla única `products`)

- `supabase.sql` → crea la tabla en Supabase (SQL Editor).
- `backend/` → API FastAPI (GET y POST `/api/v1/products`). Se despliega en Render.
- `frontend/` → React + Vite + Tailwind + visor 3D (Three.js). Se despliega en Vercel.

## Probar en tu computadora
Backend (PowerShell):
    cd backend
    python -m venv venv
    venv\Scripts\activate
    python -m pip install -r requirements.txt
    copy .env.example .env      (y pon tu DATABASE_URL real)
    uvicorn main:app --reload --port 8000
    -> abrir http://127.0.0.1:8000/docs

Frontend (otra ventana):
    cd frontend
    npm install
    npm run dev
    -> abrir http://localhost:5173

## Render (backend)
Root Directory: backend · Runtime: Python
Build: pip install -r requirements.txt
Start: uvicorn main:app --host 0.0.0.0 --port $PORT
Env: DATABASE_URL (y opcional SLACK_WEBHOOK_URL)

## Vercel (frontend)
Root Directory: frontend · Framework: Vite
Env: VITE_API_URL = URL de Render (sin barra final)
