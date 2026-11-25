import sqlite3

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException # type: ignore

from database import get_db, init_db
import schemas


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # cria as tabelas na primeira execução
    yield


app = FastAPI(title="Controle de Estoque e EPIs", version="1.0.0", lifespan=lifespan)


def buscar_ou_404(con: sqlite3.Connection, tabela: str, id_: int, nome: str) -> sqlite3.Row:
    # 'tabela' vem sempre do nosso código, nunca do usuário
    row = con.execute(f"SELECT * FROM {tabela} WHERE id = ?", (id_,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"{nome} não encontrado(a).")
    return row


# =====================================================
# Funcionários
# =====================================================
@app.post("/funcionarios", response_model=schemas.Funcionario, status_code=201, tags=["Funcionários"])
def criar_funcionario(dados: schemas.FuncionarioIn, con: sqlite3.Connection = Depends(get_db)):
    try:
        cur = con.execute(
            "INSERT INTO funcionarios (nome, matricula, setor) VALUES (?, ?, ?)",
            (dados.nome, dados.matricula, dados.setor),
        )
        con.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Já existe um funcionário com essa matrícula.")
    return dict(buscar_ou_404(con, "funcionarios", cur.lastrowid, "Funcionário"))


@app.get("/funcionarios", response_model=list[schemas.Funcionario], tags=["Funcionários"])
def listar_funcionarios(con: sqlite3.Connection = Depends(get_db)):
    rows = con.execute("SELECT * FROM funcionarios WHERE ativo = 1 ORDER BY nome").fetchall()
    return [dict(r) for r in rows]


# =====================================================
# Itens (materiais e EPIs)
# =====================================================
@app.post("/itens", response_model=schemas.Item, status_code=201, tags=["Itens"])
def criar_item(dados: schemas.ItemIn, con: sqlite3.Connection = Depends(get_db)):
    cur = con.execute(
        "INSERT INTO itens (nome, tipo, unidade, estoque_minimo, ca) VALUES (?, ?, ?, ?, ?)",
        (dados.nome, dados.tipo, dados.unidade, dados.estoque_minimo, dados.ca),
    )
    con.commit()
    return dict(buscar_ou_404(con, "itens", cur.lastrowid, "Item"))


@app.get("/itens", response_model=list[schemas.Item], tags=["Itens"])
def listar_itens(tipo: Optional[str] = None, con: sqlite3.Connection = Depends(get_db)):
    if tipo:
        rows = con.execute(
            "SELECT * FROM itens WHERE ativo = 1 AND tipo = ? ORDER BY nome", (tipo.upper(),)
        ).fetchall()
    else:
        rows = con.execute("SELECT * FROM itens WHERE ativo = 1 ORDER BY nome").fetchall()
    return [dict(r) for r in rows]


# Esta rota precisa vir ANTES de /itens/{item_id}, senão "estoque-baixo" seria tratado como id
@app.get("/itens/estoque-baixo", response_model=list[schemas.Item], tags=["Itens"])
def itens_estoque_baixo(con: sqlite3.Connection = Depends(get_db)):
    rows = con.execute(
        "SELECT * FROM itens WHERE id IN (SELECT id FROM v_estoque_baixo) ORDER BY nome"
    ).fetchall()
    return [dict(r) for r in rows]


@app.get("/itens/{item_id}", response_model=schemas.Item, tags=["Itens"])
def obter_item(item_id: int, con: sqlite3.Connection = Depends(get_db)):
    return dict(buscar_ou_404(con, "itens", item_id, "Item"))


# =====================================================
# Demandas de serviço
# =====================================================
@app.post("/demandas", response_model=schemas.Demanda, status_code=201, tags=["Demandas"])
def criar_demanda(dados: schemas.DemandaIn, con: sqlite3.Connection = Depends(get_db)):
    if dados.responsavel_id is not None:
        buscar_ou_404(con, "funcionarios", dados.responsavel_id, "Responsável")
    cur = con.execute(
        "INSERT INTO demandas (titulo, descricao, responsavel_id) VALUES (?, ?, ?)",
        (dados.titulo, dados.descricao, dados.responsavel_id),
    )
    con.commit()
    return dict(buscar_ou_404(con, "demandas", cur.lastrowid, "Demanda"))


@app.get("/demandas", response_model=list[schemas.Demanda], tags=["Demandas"])
def listar_demandas(status: Optional[str] = None, con: sqlite3.Connection = Depends(get_db)):
    if status:
        rows = con.execute(
            "SELECT * FROM demandas WHERE status = ? ORDER BY id DESC", (status.upper(),)
        ).fetchall()
    else:
        rows = con.execute("SELECT * FROM demandas ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


@app.patch("/demandas/{demanda_id}/status", response_model=schemas.Demanda, tags=["Demandas"])
def atualizar_status(demanda_id: int, dados: schemas.StatusUpdate, con: sqlite3.Connection = Depends(get_db)):
    buscar_ou_404(con, "demandas", demanda_id, "Demanda")
    if dados.status == "CONCLUIDA":
        con.execute(
            "UPDATE demandas SET status = ?, concluida_em = datetime('now', 'localtime') WHERE id = ?",
            (dados.status, demanda_id),
        )
    else:
        con.execute(
            "UPDATE demandas SET status = ?, concluida_em = NULL WHERE id = ?",
            (dados.status, demanda_id),
        )
    con.commit()
    return dict(buscar_ou_404(con, "demandas", demanda_id, "Demanda"))


# =====================================================
# Movimentações (entrada, retirada, devolução)
# =====================================================
@app.post("/movimentacoes", response_model=schemas.MovimentacaoOut, status_code=201, tags=["Movimentações"])
def registrar_movimentacao(dados: schemas.MovimentacaoIn, con: sqlite3.Connection = Depends(get_db)):
    buscar_ou_404(con, "itens", dados.item_id, "Item")
    if dados.funcionario_id is not None:
        buscar_ou_404(con, "funcionarios", dados.funcionario_id, "Funcionário")
    if dados.demanda_id is not None:
        buscar_ou_404(con, "demandas", dados.demanda_id, "Demanda")

    try:
        cur = con.execute(
            """INSERT INTO movimentacoes
                   (item_id, funcionario_id, demanda_id, tipo, quantidade, observacao)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                dados.item_id,
                dados.funcionario_id,
                dados.demanda_id,
                dados.tipo,
                dados.quantidade,
                dados.observacao,
            ),
        )
        con.commit()
    except sqlite3.IntegrityError as erro:
        # As regras do banco (estoque insuficiente, retirada sem funcionário) chegam aqui
        con.rollback()
        raise HTTPException(status_code=400, detail=str(erro))

    item = buscar_ou_404(con, "itens", dados.item_id, "Item")
    return {
        "id": cur.lastrowid,
        "item_id": dados.item_id,
        "tipo": dados.tipo,
        "quantidade": dados.quantidade,
        "estoque_atual": item["quantidade_estoque"],
    }


@app.get("/movimentacoes", response_model=list[schemas.Historico], tags=["Movimentações"])
def listar_movimentacoes(
    funcionario_id: Optional[int] = None,
    item_id: Optional[int] = None,
    demanda_id: Optional[int] = None,
    con: sqlite3.Connection = Depends(get_db),
):
    """Histórico de movimentações. Filtros opcionais por funcionário, item ou demanda."""
    sql = """
        SELECT m.id, m.data_hora, m.tipo, i.nome AS item, i.tipo AS tipo_item,
               m.quantidade, f.nome AS funcionario, d.titulo AS demanda
          FROM movimentacoes m
          JOIN itens i             ON i.id = m.item_id
          LEFT JOIN funcionarios f ON f.id = m.funcionario_id
          LEFT JOIN demandas d     ON d.id = m.demanda_id
         WHERE 1 = 1
    """
    params: list = []
    if funcionario_id is not None:
        sql += " AND m.funcionario_id = ?"
        params.append(funcionario_id)
    if item_id is not None:
        sql += " AND m.item_id = ?"
        params.append(item_id)
    if demanda_id is not None:
        sql += " AND m.demanda_id = ?"
        params.append(demanda_id)
    sql += " ORDER BY m.data_hora DESC, m.id DESC"
    return [dict(r) for r in con.execute(sql, params).fetchall()]
