-- =====================================================
-- Sistema de Controle de Estoque e EPIs (SQLite)
-- =====================================================
PRAGMA foreign_keys = ON;

-- Funcionários que podem retirar materiais e EPIs
CREATE TABLE IF NOT EXISTS funcionarios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL,
    matricula   TEXT    NOT NULL UNIQUE,
    setor       TEXT,
    ativo       INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

-- Materiais e EPIs no mesmo estoque único
CREATE TABLE IF NOT EXISTS itens (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nome                TEXT    NOT NULL,
    tipo                TEXT    NOT NULL CHECK (tipo IN ('MATERIAL', 'EPI')),
    unidade             TEXT    NOT NULL DEFAULT 'un',
    quantidade_estoque  INTEGER NOT NULL DEFAULT 0 CHECK (quantidade_estoque >= 0),
    estoque_minimo      INTEGER NOT NULL DEFAULT 0 CHECK (estoque_minimo >= 0),
    ca                  TEXT,   -- Certificado de Aprovação (apenas para EPI)
    ativo               INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

-- Demandas de serviço
CREATE TABLE IF NOT EXISTS demandas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo         TEXT    NOT NULL,
    descricao      TEXT,
    status         TEXT    NOT NULL DEFAULT 'ABERTA'
                   CHECK (status IN ('ABERTA', 'EM_ANDAMENTO', 'CONCLUIDA', 'CANCELADA')),
    responsavel_id INTEGER REFERENCES funcionarios(id),
    criada_em      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    concluida_em   TEXT
);

-- Todo movimento do estoque: entrada, retirada ou devolução
CREATE TABLE IF NOT EXISTS movimentacoes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id         INTEGER NOT NULL REFERENCES itens(id),
    funcionario_id  INTEGER REFERENCES funcionarios(id),  -- quem pegou/devolveu
    demanda_id      INTEGER REFERENCES demandas(id),      -- opcional
    tipo            TEXT    NOT NULL CHECK (tipo IN ('ENTRADA', 'RETIRADA', 'DEVOLUCAO')),
    quantidade      INTEGER NOT NULL CHECK (quantidade > 0),
    data_hora       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    observacao      TEXT
);

CREATE INDEX IF NOT EXISTS idx_mov_item        ON movimentacoes(item_id);
CREATE INDEX IF NOT EXISTS idx_mov_funcionario ON movimentacoes(funcionario_id);
CREATE INDEX IF NOT EXISTS idx_mov_demanda     ON movimentacoes(demanda_id);

-- Retirada exige funcionário identificado
CREATE TRIGGER IF NOT EXISTS trg_retirada_exige_funcionario
BEFORE INSERT ON movimentacoes
WHEN NEW.tipo = 'RETIRADA' AND NEW.funcionario_id IS NULL
BEGIN
    SELECT RAISE(ABORT, 'Retirada exige um funcionario.');
END;

-- Bloqueia retirada maior que o estoque disponível
CREATE TRIGGER IF NOT EXISTS trg_bloqueia_estoque_insuficiente
BEFORE INSERT ON movimentacoes
WHEN NEW.tipo = 'RETIRADA'
 AND NEW.quantidade > (SELECT quantidade_estoque FROM itens WHERE id = NEW.item_id)
BEGIN
    SELECT RAISE(ABORT, 'Estoque insuficiente para esta retirada.');
END;

-- Atualiza o estoque automaticamente após cada movimentação
CREATE TRIGGER IF NOT EXISTS trg_atualiza_estoque
AFTER INSERT ON movimentacoes
BEGIN
    UPDATE itens
       SET quantidade_estoque = quantidade_estoque
           + CASE WHEN NEW.tipo = 'RETIRADA' THEN -NEW.quantidade ELSE NEW.quantidade END
     WHERE id = NEW.item_id;
END;

-- Itens com estoque abaixo (ou igual) ao mínimo
CREATE VIEW IF NOT EXISTS v_estoque_baixo AS
SELECT id, nome, tipo, quantidade_estoque, estoque_minimo
  FROM itens
 WHERE ativo = 1
   AND quantidade_estoque <= estoque_minimo;

-- Histórico legível de movimentações
CREATE VIEW IF NOT EXISTS v_historico AS
SELECT m.id, m.data_hora, m.tipo, i.nome AS item, i.tipo AS tipo_item,
       m.quantidade, f.nome AS funcionario, d.titulo AS demanda
  FROM movimentacoes m
  JOIN itens i             ON i.id = m.item_id
  LEFT JOIN funcionarios f ON f.id = m.funcionario_id
  LEFT JOIN demandas d     ON d.id = m.demanda_id
 ORDER BY m.data_hora DESC;
