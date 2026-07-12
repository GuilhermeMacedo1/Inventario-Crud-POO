from enum import Enum
import sqlite3

class TipoAtivo(Enum):
    NOTEBOOK = 1
    SERVIDOR = 2
    ROTEADOR = 3
    SOFTWARE = 4
    APLICACAO_WEB = 5

# ── Requisito 11 (bônus): banco de dados SQLite ───────────────────────────────
def conectar():
    con = sqlite3.connect("ativos.db")
    con.execute("""
        CREATE TABLE IF NOT EXISTS ativos (
            id          INTEGER PRIMARY KEY,
            nome        TEXT,
            responsavel TEXT,
            setor       TEXT,
            tipo        TEXT
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS vulnerabilidades (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            id_ativo INTEGER,
            descricao  TEXT,
            categoria  TEXT,
            severidade TEXT,
            status     TEXT
        )
    """)
    con.commit()
    return con

# ── Requisito 9: dicionário para buscas rápidas ───────────────────────────────
def carregar_dict(con):
    ativos = {}
    for row in con.execute("SELECT id, nome, responsavel, setor, tipo FROM ativos"):
        ativos[row[0]] = {
            "id": row[0],
            "nome": row[1],
            "responsavel": row[2],
            "setor": row[3],
            "tipo": row[4]
        }
    return ativos

# ── Requisito 3: cadastrar ativo ──────────────────────────────────────────────
def cadastrar(con, ativos):
    print("\n=== Cadastrar ativo ===")

    try:
        id_ativo = int(input("ID do ativo (número): "))
    except ValueError:
        print("ID inválido, precisa ser um número.")
        return

    if id_ativo in ativos:
        print("Esse ID já existe!")
        return

    nome = input("Nome/hostname: ").strip()
    if not nome:
        print("Nome não pode ser vazio.")
        return

    responsavel = input("Responsável: ").strip()
    setor = input("Setor/localização: ").strip()

    print("Tipos disponíveis:")
    for t in TipoAtivo:
        print(f"  {t.value} - {t.name}")

    try:
        tipo_num = int(input("Escolha o tipo (número): "))
        tipo = TipoAtivo(tipo_num).name
    except (ValueError, KeyError):
        print("Tipo inválido.")
        return

    con.execute(
        "INSERT INTO ativos VALUES (?, ?, ?, ?, ?)",
        (id_ativo, nome, responsavel, setor, tipo)
    )
    con.commit()

    ativos[id_ativo] = {"id": id_ativo, "nome": nome, "responsavel": responsavel, "setor": setor, "tipo": tipo}
    print("Ativo cadastrado com sucesso!")

# ── Requisito 4: buscar ativo ─────────────────────────────────────────────────
def buscar(con, ativos):
    print("\n=== Buscar ativo ===")
    print("1 - Buscar por ID")
    print("2 - Buscar por nome")
    op = input("Opção: ").strip()

    if op == "1":
        try:
            id_ativo = int(input("ID: "))
        except ValueError:
            print("ID inválido.")
            return

        # usa o dict para busca rápida (requisito 9)
        if id_ativo in ativos:
            a = ativos[id_ativo]
            print(f"\nID: {a['id']}")
            print(f"Nome: {a['nome']}")
            print(f"Responsável: {a['responsavel']}")
            print(f"Setor: {a['setor']}")
            print(f"Tipo: {a['tipo']}")
        else:
            print("Ativo não encontrado.")

    elif op == "2":
        nome = input("Nome: ").strip()
        encontrou = False
        for a in ativos.values():
            if nome.lower() in a["nome"].lower():
                print(f"\nID: {a['id']} | Nome: {a['nome']} | Setor: {a['setor']}")
                encontrou = True
        if not encontrou:
            print("Nenhum ativo encontrado.")
    else:
        print("Opção inválida.")

# ── Requisito 5: atualizar ativo ──────────────────────────────────────────────
def atualizar(con, ativos):
    print("\n=== Atualizar ativo ===")

    try:
        id_ativo = int(input("ID do ativo: "))
    except ValueError:
        print("ID inválido.")
        return

    if id_ativo not in ativos:
        print("Ativo não encontrado.")
        return

    a = ativos[id_ativo]
    print(f"Ativo atual: {a['nome']} | {a['responsavel']} | {a['setor']}")
    print("(deixe em branco para não alterar)")

    novo_nome = input(f"Novo nome [{a['nome']}]: ").strip()
    novo_resp = input(f"Novo responsável [{a['responsavel']}]: ").strip()
    novo_setor = input(f"Novo setor [{a['setor']}]: ").strip()

    if novo_nome:   a["nome"] = novo_nome
    if novo_resp:   a["responsavel"] = novo_resp
    if novo_setor:  a["setor"] = novo_setor

    con.execute(
        "UPDATE ativos SET nome=?, responsavel=?, setor=? WHERE id=?",
        (a["nome"], a["responsavel"], a["setor"], id_ativo)
    )
    con.commit()
    print("Ativo atualizado!")

# ── Requisito 6: deletar ativo ────────────────────────────────────────────────
def deletar(con, ativos):
    print("\n=== Deletar ativo ===")

    try:
        id_ativo = int(input("ID do ativo: "))
    except ValueError:
        print("ID inválido.")
        return

    if id_ativo not in ativos:
        print("Ativo não encontrado.")
        return

    confirma = input(f"Tem certeza que quer deletar o ativo {id_ativo}? (s/n): ")
    if confirma.lower() != "s":
        print("Cancelado.")
        return

    con.execute("DELETE FROM vulnerabilidades WHERE id_ativo = ?", (id_ativo,))
    con.execute("DELETE FROM ativos WHERE id = ?", (id_ativo,))
    con.commit()
    del ativos[id_ativo]
    print("Ativo e suas vulnerabilidades foram removidos.")

# ── Requisito 7: cadastrar vulnerabilidade ────────────────────────────────────
def adicionar_vulnerabilidade(con, ativos):
    print("\n=== Adicionar vulnerabilidade ===")

    try:
        id_ativo = int(input("ID do ativo: "))
    except ValueError:
        print("ID inválido.")
        return

    if id_ativo not in ativos:
        print("Ativo não encontrado.")
        return

    descricao = input("Descrição da vulnerabilidade: ").strip()
    if not descricao:
        print("Descrição não pode ser vazia.")
        return

    categoria = input("Categoria (ex: configuração, software, acesso): ").strip()

    print("Severidade: 1-baixa  2-media  3-alta  4-critica")
    severidades = ["baixa", "media", "alta", "critica"]
    try:
        sev = int(input("Escolha: ")) - 1
        severidade = severidades[sev]
    except (ValueError, IndexError):
        print("Severidade inválida.")
        return

    print("Status: 1-aberta  2-em tratamento  3-corrigida  4-aceita")
    status_opcoes = ["aberta", "em tratamento", "corrigida", "aceita"]
    try:
        st = int(input("Escolha: ")) - 1
        status = status_opcoes[st]
    except (ValueError, IndexError):
        print("Status inválido.")
        return

    con.execute(
        "INSERT INTO vulnerabilidades (id_ativo, descricao, categoria, severidade, status) VALUES (?,?,?,?,?)",
        (id_ativo, descricao, categoria, severidade, status)
    )
    con.commit()
    print("Vulnerabilidade adicionada!")

# ── Requisito 8: ver vulnerabilidades ────────────────────────────────────────
def ver_vulnerabilidades(con, ativos):
    print("\n=== Vulnerabilidades ===")

    try:
        id_ativo = int(input("ID do ativo: "))
    except ValueError:
        print("ID inválido.")
        return

    if id_ativo not in ativos:
        print("Ativo não encontrado.")
        return

    rows = con.execute(
        "SELECT descricao, categoria, severidade, status FROM vulnerabilidades WHERE id_ativo = ?",
        (id_ativo,)
    ).fetchall()

    if not rows:
        print("Este ativo não tem vulnerabilidades registradas.")
        return

    print(f"\nVulnerabilidades do ativo {id_ativo}:")
    for i, r in enumerate(rows, 1):
        print(f"\n  [{i}] {r[0]}")
        print(f"      Categoria : {r[1]}")
        print(f"      Severidade: {r[2]}")
        print(f"      Status    : {r[3]}")

# ── Requisito 1: menu principal ───────────────────────────────────────────────
def menu():
    con = conectar()
    ativos = carregar_dict(con)

    while True:
        print("\n=============================")
        print("  INVENTÁRIO DE SEGURANÇA")
        print("=============================")
        print("1 - Cadastrar ativo")
        print("2 - Buscar ativo")
        print("3 - Atualizar ativo")
        print("4 - Deletar ativo")
        print("5 - Adicionar vulnerabilidade")
        print("6 - Ver vulnerabilidades")
        print("0 - Sair")

        op = input("\nEscolha uma opção: ").strip()

        if op == "1":
            cadastrar(con, ativos)
        elif op == "2":
            buscar(con, ativos)
        elif op == "3":
            atualizar(con, ativos)
        elif op == "4":
            deletar(con, ativos)
        elif op == "5":
            adicionar_vulnerabilidade(con, ativos)
        elif op == "6":
            ver_vulnerabilidades(con, ativos)
        elif op == "0":
            print("Saindo...")
            con.close()
            break
        else:
            print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    menu()
