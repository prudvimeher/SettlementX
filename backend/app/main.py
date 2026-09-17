from fastapi import FastAPI

from app.db.database import Base, engine
from app.db import models


Base.metadata.create_all(bind=engine)

app = FastAPI(title="SettlementX")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}