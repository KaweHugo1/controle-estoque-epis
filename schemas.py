from typing import Literal, Optional

from pydantic import BaseModel, Field # type: ignore


# ---------- Funcionários ----------
class FuncionarioIn(BaseModel):
    nome: str = Field(min_length=1)
    matricula: str = Field(min_length=1)
    setor: Optional[str] = None


class Funcionario(FuncionarioIn):
    id: int
    ativo: bool


# ---------- Itens (materiais e EPIs) ----------
class ItemIn(BaseModel):
    nome: str = Field(min_length=1)
    tipo: Literal["MATERIAL", "EPI"]
    unidade: str = "un"
    estoque_minimo: int = Field(default=0, ge=0)
    ca: Optional[str] = None  # Certificado de Aprovação (EPI)


class Item(ItemIn):
    id: int
    quantidade_estoque: int
    ativo: bool


# ---------- Demandas de serviço ----------
StatusDemanda = Literal["ABERTA", "EM_ANDAMENTO", "CONCLUIDA", "CANCELADA"]


class DemandaIn(BaseModel):
    titulo: str = Field(min_length=1)
    descricao: Optional[str] = None
    responsavel_id: Optional[int] = None


class Demanda(DemandaIn):
    id: int
    status: StatusDemanda
    criada_em: str
    concluida_em: Optional[str] = None


class StatusUpdate(BaseModel):
    status: StatusDemanda


# ---------- Movimentações ----------
class MovimentacaoIn(BaseModel):
    item_id: int
    tipo: Literal["ENTRADA", "RETIRADA", "DEVOLUCAO"]
    quantidade: int = Field(gt=0)
    funcionario_id: Optional[int] = None  # obrigatório na RETIRADA
    demanda_id: Optional[int] = None
    observacao: Optional[str] = None


class MovimentacaoOut(BaseModel):
    id: int
    item_id: int
    tipo: str
    quantidade: int
    estoque_atual: int


class Historico(BaseModel):
    id: int
    data_hora: str
    tipo: str
    item: str
    tipo_item: str
    quantidade: int
    funcionario: Optional[str] = None
    demanda: Optional[str] = None
