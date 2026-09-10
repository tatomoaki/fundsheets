from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import asset_allocations, chat, compare, fees, funds, holdings, performance

app = FastAPI(
    title="Minimum Disclosure Document Analyser"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")
api_router.include_router(funds.router)
api_router.include_router(fees.router)
api_router.include_router(holdings.router)
api_router.include_router(asset_allocations.router)
api_router.include_router(compare.router)
api_router.include_router(performance.router)
api_router.include_router(chat.router)

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Fund sheet analyser"}
