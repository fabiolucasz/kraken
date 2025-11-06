from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from typing import List, Dict, Any

app = FastAPI()

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/acoes_ranking")
async def get_acoes_ranking(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Retorna todos os dados da tabela gold.acoes_ranking.
    """
    result = db.execute(text("SELECT * FROM gold.acoes_ranking"))
    acoes_ranking = [dict(row._mapping) for row in result]
    return acoes_ranking

@app.get("/fiis_ranking")
async def get_fiis_ranking(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Retorna todos os dados da tabela gold.fiis_ranking.
    """
    result = db.execute(text("SELECT * FROM gold.fiis_ranking"))
    fiis_ranking = [dict(row._mapping) for row in result]
    return fiis_ranking


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)