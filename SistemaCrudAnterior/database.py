import sqlite3
from ativo import Ativo, TipoAtivo
from vulnerabilidade import Vulnerabilidade

DB_PATH = "inventario.db"


def conectar():
    return sqlite3.connect(DB_PATH)


def inicializar_banco():
    """Cria as tabelas se ainda não existirem."""
    with conectar() as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ativos (
                id          INTEGER PRIMARY KEY,
                nome        TEXT    NOT NULL,
                responsavel TEXT    NOT NULL,
                setor       TEXT    NOT NULL,
                tipo        TEXT    NOT NULL,
                descricao   TEXT    DEFAULT ''
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vulnerabilidades (
                id_vuln    INTEGER PRIMARY KEY AUTOINCREMENT,
                id_ativo   INTEGER NOT NULL,
                descricao  TEXT    NOT NULL,
                categoria  TEXT    NOT NULL,
                severidade TEXT    NOT NULL,
                status     TEXT    NOT NULL,
                FOREIGN KEY (id_ativo) REFERENCES ativos(id)
            )
        """)
        con.commit()


def inserir_ativo(ativo: Ativo):
    with conectar() as con:
        con.execute(
            "INSERT INTO ativos VALUES (?, ?, ?, ?, ?, ?)",
            (ativo.id, ativo.nome, ativo.responsavel,
             ativo.setor, ativo.tipo.name, ativo.descricao)
        )
        con.commit()


def buscar_por_id(id_ativo: int):
    with conectar() as con:
        row = con.execute(
            "SELECT * FROM ativos WHERE id = ?", (id_ativo,)
        ).fetchone()
    return _row_para_ativo(row, id_ativo) if row else None


def buscar_por_nome(nome: str):
    with conectar() as con:
        rows = con.execute(
            "SELECT * FROM ativos WHERE LOWER(nome) LIKE ?",
            (f"%{nome.lower()}%",)
        ).fetchall()
    return [_row_para_ativo(r, r[0]) for r in rows]


def listar_todos():
    with conectar() as con:
        rows = con.execute("SELECT * FROM ativos ORDER BY id").fetchall()
    return [_row_para_ativo(r, r[0]) for r in rows]


def atualizar_ativo(ativo: Ativo):
    with conectar() as con:
        con.execute(
            """UPDATE ativos
               SET nome=?, responsavel=?, setor=?, tipo=?, descricao=?
               WHERE id=?""",
            (ativo.nome, ativo.responsavel, ativo.setor,
             ativo.tipo.name, ativo.descricao, ativo.id)
        )
        con.commit()


def deletar_ativo(id_ativo: int):
    with conectar() as con:
        con.execute("DELETE FROM vulnerabilidades WHERE id_ativo = ?", (id_ativo,))
        con.execute("DELETE FROM ativos WHERE id = ?", (id_ativo,))
        con.commit()


def id_existe(id_ativo: int) -> bool:
    with conectar() as con:
        row = con.execute(
            "SELECT 1 FROM ativos WHERE id = ?", (id_ativo,)
        ).fetchone()
    return row is not None


def inserir_vulnerabilidade(id_ativo: int, v: Vulnerabilidade):
    with conectar() as con:
        con.execute(
            "INSERT INTO vulnerabilidades (id_ativo, descricao, categoria, severidade, status) VALUES (?,?,?,?,?)",
            (id_ativo, v.descrição, v.categoria, v.severidade, v.status)
        )
        con.commit()


def buscar_vulnerabilidades(id_ativo: int):
    with conectar() as con:
        rows = con.execute(
            "SELECT descrição, categoria, severidade, status FROM vulnerabilidades WHERE id_ativo = ?",
            (id_ativo,)
        ).fetchall()
    return [Vulnerabilidade(*r) for r in rows]


def _row_para_ativo(row, id_ativo: int) -> Ativo:
    """Converte uma linha do banco em objeto Ativo já com vulnerabilidades."""
    a = Ativo(
        id=row[0],
        nome=row[1],
        responsavel=row[2],
        setor=row[3],
        tipo=TipoAtivo[row[4]],
        descricao=row[5]
    )
    a.vulnerabilidades = buscar_vulnerabilidades(id_ativo)
    return a


def carregar_em_dict() -> dict:
    """Retorna todos os ativos indexados por ID (requisito R9 — dict/hash map)."""
    return {a.id: a for a in listar_todos()}
