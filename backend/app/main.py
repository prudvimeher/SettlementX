from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.db import models
from app.routes.trades import router as trades_router
from app.routes.external import router as external_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SettlementX")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(trades_router)
app.include_router(external_router)

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}