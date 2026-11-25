import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "estoque.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection() -> sqlite3.Connection:
    # check_same_thread=False: o FastAPI pode usar threads diferentes na mesma requisição
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db() -> None:
    """Cria as tabelas, triggers e views caso ainda não existam."""
    con = get_connection()
    try:
        con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        con.commit()
    finally:
        con.close()


def get_db():
    """Dependência do FastAPI: abre uma conexão por requisição e fecha no final."""
    con = get_connection()
    try:
        yield con
    finally:
        con.close()
