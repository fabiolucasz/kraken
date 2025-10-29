from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from typing import List, Dict, Any

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/acoes_info")
async def get_acoes_info(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    result = db.execute(text("SELECT * FROM bronze.acoes_info"))
    acoes_info = [dict(row._mapping) for row in result]
    return acoes_info

@app.get("/acoes_kpi")
async def get_acoes_kpi(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    result = db.execute(text("SELECT * FROM bronze.acoes_kpi"))
    acoes_kpi = [dict(row._mapping) for row in result]
    return acoes_kpi

@app.get("/acoes_indicadores")
async def get_acoes_indicadores(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    result = db.execute(text("SELECT * FROM bronze.acoes_indicadores"))
    acoes_indicadores = [dict(row._mapping) for row in result]
    return acoes_indicadores

@app.get("/acoes_img")
async def get_acoes_img(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    result = db.execute(text("SELECT * FROM bronze.acoes_img"))
    acoes_img = [dict(row._mapping) for row in result]
    return acoes_img

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)