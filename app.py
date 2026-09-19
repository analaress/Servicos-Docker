import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
DATABASE_PATH = DATA_DIR / "notas.db"
app = FastAPI(title="Notas API")

class NotaEntrada(BaseModel):
    texto: str

def inicializar_banco() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DATABASE_PATH)) as conexao:
        conexao.execute("CREATE TABLE IF NOT EXISTS notas (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT NOT NULL, criada_em TEXT NOT NULL)")
        conexao.commit()

@app.on_event("startup")
def startup() -> None:
    inicializar_banco()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/notas", status_code=201)
def criar_nota(nota: NotaEntrada) -> dict:
    texto = nota.texto.strip()
    if not texto:
        raise HTTPException(status_code=400, detail="O texto da nota não pode estar vazio")
    criada_em = datetime.now(timezone.utc).isoformat()
    with closing(sqlite3.connect(DATABASE_PATH)) as conexao:
        cursor = conexao.execute("INSERT INTO notas (texto, criada_em) VALUES (?, ?)", (texto, criada_em))
        conexao.commit()
        return {"id": cursor.lastrowid, "texto": texto, "criada_em": criada_em}

@app.get("/notas")
def listar_notas() -> list[dict]:
    with closing(sqlite3.connect(DATABASE_PATH)) as conexao:
        conexao.row_factory = sqlite3.Row
        linhas = conexao.execute("SELECT id, texto, criada_em FROM notas ORDER BY id").fetchall()
        return [dict(linha) for linha in linhas]
