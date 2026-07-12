from ativo import Ativo, TipoAtivo
from vulnerabilidade import Vulnerabilidade
import database as db


def _ler_inteiro(prompt: str) -> int:
    while True:
        try:
            valor = input(prompt).strip()
            if not valor:
                print("  ✗ Campo obrigatório.")
                continue
            return int(valor)
        except ValueError:
            print("  ✗ Digite apenas números inteiros.")


def _ler_texto(prompt: str, obrigatorio: bool = True) -> str:
    while True:
        valor = input(prompt).strip()
        if obrigatorio and not valor:
            print("  ✗ Campo obrigatório.")
            continue
        return valor


def _escolher_opcao(prompt: str, opcoes: list) -> str:
    for i, op in enumerate(opcoes, 1):
        print(f"    {i}. {op}")
    while True:
        try:
            idx = int(input(prompt).strip()) - 1
            if 0 <= idx < len(opcoes):
                return opcoes[idx]
            print(f"  ✗ Escolha entre 1 e {len(opcoes)}.")
        except ValueError:
            print("  ✗ Digite o número da opção.")


def _escolher_tipo() -> TipoAtivo:
    tipos = list(TipoAtivo)
    print("\n  Tipos de ativo disponíveis:")
    for t in tipos:
        print(f"    {t.value}. {t.name.replace('_', ' ')}")
    while True:
        try:
            codigo = int(input("  Código do tipo: ").strip())
            return TipoAtivo(codigo)
        except (ValueError, KeyError):
            print(f"  ✗ Código inválido. Escolha entre 1 e {len(tipos)}.")


def _pedir_id_ativo(prompt: str = "  ID do ativo: "):
    """Lê um ID e verifica se existe no banco."""
    id_ativo = _ler_inteiro(prompt)
    ativo = db.buscar_por_id(id_ativo)
    if not ativo:
        print(f"  ✗ Nenhum ativo encontrado com ID {id_ativo}.")
        return None
    return ativo


def cadastrar(ativos: dict):
    print("\n── CADASTRAR NOVO ATIVO ─────────────────────────")

    while True:
        id_ativo = _ler_inteiro("  ID (número inteiro único): ")
        if db.id_existe(id_ativo):
            print(f"  ✗ ID {id_ativo} já está em uso. Tente outro.")
        else:
            break

    nome        = _ler_texto("  Nome / Hostname      : ")
    responsavel = _ler_texto("  Responsável          : ")
    setor       = _ler_texto("  Setor / Localização  : ")
    descricao   = _ler_texto("  Descrição (opcional) : ", obrigatorio=False)
    tipo        = _escolher_tipo()

    ativo = Ativo(id_ativo, nome, responsavel, setor, tipo, descricao)

    while True:
        add = input("\n  Deseja adicionar uma vulnerabilidade agora? (s/n): ").strip().lower()
        if add == "s":
            v = _coletar_vulnerabilidade()
            ativo.vulnerabilidades.append(v)
            db.inserir_ativo(ativo) if len(ativo.vulnerabilidades) == 1 else None
        else:
            break

    db.inserir_ativo(ativo)
    # Insere vulnerabilidades coletadas
    for v in ativo.vulnerabilidades:
        db.inserir_vulnerabilidade(id_ativo, v)

    ativos[id_ativo] = ativo
    print(f"\n  ✓ Ativo #{id_ativo} cadastrado com sucesso!")


def buscar(ativos: dict):
    print("\n── BUSCAR ATIVO ─────────────────────────────────")
    print("  1. Buscar por ID")
    print("  2. Buscar por nome / hostname")
    print("  3. Listar todos")
    opcao = input("  Opção: ").strip()

    if opcao == "1":
        id_ativo = _ler_inteiro("  ID do ativo: ")
        # Tenta o dict em memória primeiro (R9)
        ativo = ativos.get(id_ativo) or db.buscar_por_id(id_ativo)
        if ativo:
            ativo.exibir()
        else:
            print(f"  ✗ Nenhum ativo com ID {id_ativo}.")

    elif opcao == "2":
        nome = _ler_texto("  Nome / hostname: ")
        resultados = db.buscar_por_nome(nome)
        if resultados:
            print(f"\n  {len(resultados)} resultado(s) encontrado(s):")
            for a in resultados:
                a.exibir()
        else:
            print("  ✗ Nenhum ativo encontrado.")

    elif opcao == "3":
        todos = list(ativos.values()) or db.listar_todos()
        if todos:
            print(f"\n  Total: {len(todos)} ativo(s) cadastrado(s)")
            for a in todos:
                a.exibir()
        else:
            print("  ✗ Nenhum ativo cadastrado ainda.")
    else:
        print("  ✗ Opção inválida.")


def atualizar(ativos: dict):
    print("\n── ATUALIZAR ATIVO ──────────────────────────────")
    ativo = _pedir_id_ativo()
    if not ativo:
        return

    ativo.exibir()
    print("\n  Deixe em branco para manter o valor atual.\n")

    novo_nome = input(f"  Nome [{ativo.nome}]: ").strip()
    novo_resp = input(f"  Responsável [{ativo.responsavel}]: ").strip()
    novo_setor = input(f"  Setor [{ativo.setor}]: ").strip()
    novo_desc  = input(f"  Descrição [{ativo.descricao}]: ").strip()

    alterar_tipo = input("  Alterar tipo? (s/n): ").strip().lower()
    novo_tipo = _escolher_tipo() if alterar_tipo == "s" else ativo.tipo

    if novo_nome:   ativo.nome = novo_nome
    if novo_resp:   ativo.responsavel = novo_resp
    if novo_setor:  ativo.setor = novo_setor
    if novo_desc:   ativo.descricao = novo_desc
    ativo.tipo = novo_tipo

    db.atualizar_ativo(ativo)
    ativos[ativo.id] = ativo
    print(f"\n  ✓ Ativo #{ativo.id} atualizado com sucesso!")


def deletar(ativos: dict):
    print("\n── DELETAR ATIVO ────────────────────────────────")
    ativo = _pedir_id_ativo()
    if not ativo:
        return

    ativo.exibir()
    confirmacao = input(f"\n  ⚠ Confirma remoção do ativo #{ativo.id} e suas {len(ativo.vulnerabilidades)} vulnerabilidade(s)? (s/n): ").strip().lower()
    if confirmacao == "s":
        db.deletar_ativo(ativo.id)
        ativos.pop(ativo.id, None)
        print(f"\n  ✓ Ativo #{ativo.id} removido com sucesso!")
    else:
        print("  Operação cancelada.")

def _coletar_vulnerabilidade() -> Vulnerabilidade:
    print("\n  ── Nova vulnerabilidade ──")
    descricao = _ler_texto("  Descrição  : ")
    categoria = _ler_texto("  Categoria  : ")

    print("  Severidade:")
    severidade = _escolher_opcao("  Escolha: ", Vulnerabilidade.SEVERIDADES)

    print("  Status:")
    status = _escolher_opcao("  Escolha: ", Vulnerabilidade.STATUS_OPCOES)

    return Vulnerabilidade(descricao, categoria, severidade, status)


def adicionar_vulnerabilidade(ativos: dict):
    print("\n── ADICIONAR VULNERABILIDADE ────────────────────")
    ativo = _pedir_id_ativo()
    if not ativo:
        return

    v = _coletar_vulnerabilidade()
    db.inserir_vulnerabilidade(ativo.id, v)
    ativo.vulnerabilidades.append(v)
    ativos[ativo.id] = ativo
    print(f"\n  ✓ Vulnerabilidade adicionada ao ativo #{ativo.id}!")


def ver_vulnerabilidades(ativos: dict):
    print("\n── VULNERABILIDADES DO ATIVO ────────────────────")
    ativo = _pedir_id_ativo()
    if not ativo:
        return

    vulns = db.buscar_vulnerabilidades(ativo.id)
    print(f"\n  Ativo: {ativo.nome} (#{ativo.id})")

    if not vulns:
        print("  ✓ Nenhuma vulnerabilidade registrada para este ativo.")
        return

    print(f"  {len(vulns)} vulnerabilidade(s):\n")
    for i, v in enumerate(vulns, 1):
        v.exibir(i)
        print()
