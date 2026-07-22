# Fund Sheet Analyser

Monorepo with a FastAPI backend and React + Vite frontend.

## Project Structure

```
fundsheets/
├── backend/          # FastAPI application
│   ├── src/          # Python source code
│   └── .env          # Environment variables
│  
├── frontend/         # React + Vite application
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
```

## Running the Backend

```bash
cd backend
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

All API routes are prefixed with `/api` (e.g. `/api/funds/`).

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs at `http://localhost:5173` and proxies `/api/*` requests to the backend.
