import json
import os
import shutil
from abc import ABC, abstractmethod

class Vulnerabilidade:
    def __init__(self, id_vuln, descricao, categoria, severidade, status):
        self.id = id_vuln
        self.descricao = descricao
        self.categoria = categoria
        self.severidade = severidade
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "descricao": self.descricao,
            "categoria": self.categoria,
            "severidade": self.severidade,
            "status": self.status
        }

    @staticmethod
    def from_dict(dados):
        return Vulnerabilidade(
            dados["id"], dados["descricao"], dados["categoria"],
            dados["severidade"], dados["status"]
        )

    def __str__(self):
        return (f"  VulnID {self.id} | {self.descricao} | "
                f"Categoria: {self.categoria} | Severidade: {self.severidade} | "
                f"Status: {self.status}")

class Equipamento(ABC):

    def __init__(self, id_equip, hostname, responsavel, setor):
        self.id = id_equip
        self.hostname = hostname
        self.responsavel = responsavel
        self.setor = setor
        self.vulnerabilidades = []

    @abstractmethod
    def tipo(self):
        pass

    def descricao_categoria(self):
        return "Equipamento genérico"

    def adicionar_vulnerabilidade(self, vulnerabilidade):
        self.vulnerabilidades.append(vulnerabilidade)

    def buscar_vulnerabilidade(self, id_vuln):
        for v in self.vulnerabilidades:
            if v.id == id_vuln:
                return v
        return None

    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo(),
            "hostname": self.hostname,
            "responsavel": self.responsavel,
            "setor": self.setor,
            "vulnerabilidades": [v.to_dict() for v in self.vulnerabilidades]
        }

    def __str__(self):
        return (f"[{self.id}] {self.tipo()} - {self.hostname} | "
                f"Responsável: {self.responsavel} | Setor: {self.setor} | "
                f"({self.descricao_categoria()})")


class Laptop(Equipamento):
    def tipo(self):
        return "Laptop"

    def descricao_categoria(self):
        return "Dispositivo móvel de uso individual"


class Servidor(Equipamento):
    def tipo(self):
        return "Servidor"

    def descricao_categoria(self):
        return "Equipamento crítico de infraestrutura"


class Roteador(Equipamento):
    def tipo(self):
        return "Roteador"

    def descricao_categoria(self):
        return "Equipamento de rede"


class Impressora(Equipamento):
    def tipo(self):
        return "Impressora"

    def descricao_categoria(self):
        return "Periférico compartilhado"

class FabricaEquipamento:
    _MAPA_TIPOS = {1: Laptop, 2: Servidor, 3: Roteador, 4: Impressora}
    _MAPA_NOMES = {1: "Laptop", 2: "Servidor", 3: "Roteador", 4: "Impressora"}
    _MAPA_NOME_PARA_CLASSE = {
        "Laptop": Laptop, "Servidor": Servidor,
        "Roteador": Roteador, "Impressora": Impressora
    }

    @classmethod
    def criar_por_opcao(cls, opcao, id_equip, hostname, responsavel, setor):
        classe = cls._MAPA_TIPOS.get(opcao)
        if classe is None:
            raise ValueError("Opção de tipo inválida")
        return classe(id_equip, hostname, responsavel, setor)

    @classmethod
    def criar_por_nome(cls, nome_tipo, id_equip, hostname, responsavel, setor):
        classe = cls._MAPA_NOME_PARA_CLASSE.get(nome_tipo)
        if classe is None:
            raise ValueError("Tipo inválido")
        return classe(id_equip, hostname, responsavel, setor)

    @classmethod
    def nome_do_tipo(cls, opcao):
        return cls._MAPA_NOMES.get(opcao)

class RepositorioJSON:

    def __init__(self, caminho_arquivo="dados.json"):
        self.caminho_arquivo = caminho_arquivo
        self.equipamentos = []
        self._proximo_id_equip = 1
        self._proximo_id_vuln = 1
        self._carregar()

    def _carregar(self):
        if not os.path.exists(self.caminho_arquivo):
            return
        with open(self.caminho_arquivo, "r", encoding="utf-8") as arquivo:
            try:
                dados = json.load(arquivo)
            except json.JSONDecodeError:
                dados = []

        for item in dados:
            equip = FabricaEquipamento.criar_por_nome(
                item["tipo"], item["id"], item["hostname"],
                item["responsavel"], item["setor"]
            )
            for v in item.get("vulnerabilidades", []):
                vuln = Vulnerabilidade.from_dict(v)
                equip.adicionar_vulnerabilidade(vuln)
                self._proximo_id_vuln = max(self._proximo_id_vuln, vuln.id + 1)
            self.equipamentos.append(equip)
            self._proximo_id_equip = max(self._proximo_id_equip, equip.id + 1)

    def salvar(self):
        dados = [equip.to_dict() for equip in self.equipamentos]
        with open(self.caminho_arquivo, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)

    # ---------- CRUD de Equipamentos ----------

    def criar_equipamento(self, opcao_tipo, hostname, responsavel, setor):
        equip = FabricaEquipamento.criar_por_opcao(
            opcao_tipo, self._proximo_id_equip, hostname, responsavel, setor
        )
        self.equipamentos.append(equip)
        self._proximo_id_equip += 1
        self.salvar()
        return equip

    def buscar_por_id_e_tipo(self, id_equip, tipo):
        for equip in self.equipamentos:
            if equip.id == id_equip and equip.tipo() == tipo:
                return equip
        return None

    def buscar_por_id(self, id_equip):
        for equip in self.equipamentos:
            if equip.id == id_equip:
                return equip
        return None

    def atualizar_equipamento(self, equip, hostname, responsavel, setor, nova_opcao_tipo=None):
        novo_tipo_nome = FabricaEquipamento.nome_do_tipo(nova_opcao_tipo) if nova_opcao_tipo else None

        if novo_tipo_nome and novo_tipo_nome != equip.tipo():
            novo_equip = FabricaEquipamento.criar_por_opcao(
                nova_opcao_tipo, equip.id, hostname, responsavel, setor
            )
            novo_equip.vulnerabilidades = equip.vulnerabilidades
            indice = self.equipamentos.index(equip)
            self.equipamentos[indice] = novo_equip
            equip = novo_equip
        else:
            equip.hostname = hostname
            equip.responsavel = responsavel
            equip.setor = setor

        self.salvar()
        return equip

    def deletar_equipamento(self, equip):
        self.equipamentos.remove(equip)
        self.salvar()

    def adicionar_vulnerabilidade(self, equip, descricao, categoria, severidade, status):
        vuln = Vulnerabilidade(self._proximo_id_vuln, descricao, categoria, severidade, status)
        equip.adicionar_vulnerabilidade(vuln)
        self._proximo_id_vuln += 1
        self.salvar()
        return vuln

    def buscar_equipamento_da_vulnerabilidade(self, id_vuln):
        for equip in self.equipamentos:
            if equip.buscar_vulnerabilidade(id_vuln):
                return equip
        return None

    def atualizar_vulnerabilidade(self, vuln, descricao, categoria, severidade, status):
        vuln.descricao = descricao
        vuln.categoria = categoria
        vuln.severidade = severidade
        vuln.status = status
        self.salvar()

class InterfaceConsole:
    def __init__(self, repositorio):
        self.repo = repositorio
        self.colunas = shutil.get_terminal_size().columns

    def _centralizar(self, texto):
        print(texto.center(self.colunas))

    def _ler_inteiro(self, mensagem):
        try:
            return int(input(mensagem).strip())
        except ValueError:
            print("Isso não é um número")
            return None

    def encerrar(self):
        self._centralizar("Até logo!")
        exit()

    def iniciar(self):
        self._centralizar("Bem-vindo à Security©")
        self._centralizar("*Garantimos a segurança dos seus dispositivos eletrônicos*")

        while True:
            print("""
Você já possui dispositivos cadastrados no sistema?
Pressione "y" se sim
Pressione "n" se não, ou se quiser cadastrar novos dispositivos/vulnerabilidades
Pressione "b" para sair
            """)
            escolha = input().strip().lower()

            if escolha == "b":
                self.encerrar()
            elif escolha == "y":
                self._menu_consultar()
            elif escolha == "n":
                self._menu_cadastrar()
            else:
                print("Opção inválida")

    def _menu_consultar(self):
        while True:
            print("""
Qual tipo de dispositivo você deseja consultar:
Pressione "1" para Laptop
Pressione "2" para Servidor
Pressione "3" para Roteador
Pressione "4" para Impressora
Pressione "5" para voltar
            """)
            opcao = self._ler_inteiro("")
            if opcao is None:
                continue
            if opcao == 5:
                return
            if opcao not in (1, 2, 3, 4):
                print("Essa opção não existe")
                continue
            self._consultar_por_tipo(FabricaEquipamento.nome_do_tipo(opcao))

    def _consultar_por_tipo(self, tipo):
        while True:
            id_equip = self._ler_inteiro(
                "\nInsira o ID do dispositivo que deseja consultar ou '0' para sair:\n"
            )
            if id_equip is None:
                continue
            if id_equip == 0:
                return

            equip = self.repo.buscar_por_id_e_tipo(id_equip, tipo)
            if equip is None:
                print("ID não encontrado")
                continue

            print(equip)
            self._menu_vulnerabilidades_leitura(equip)
            self._menu_operacoes(equip)

    def _menu_vulnerabilidades_leitura(self, equip):
        while True:
            escolha = input(
                "\nDeseja consultar também a lista de vulnerabilidades? (y/n):\n"
            ).strip().lower()
            if escolha == "n":
                return
            elif escolha == "y":
                if equip.vulnerabilidades:
                    for vuln in equip.vulnerabilidades:
                        print(vuln)
                else:
                    print("Não há vulnerabilidades cadastradas para este ID")
                return
            else:
                print("Opção inválida")

    def _menu_operacoes(self, equip):
        while True:
            print("""
Deseja realizar alguma operação com esses dados?
Pressione "u" para atualizar os dados
Pressione "d" para deletar os dados
Pressione "r" para voltar à seleção de dispositivo
            """)
            escolha = input().strip().lower()

            if escolha == "r":
                return
            elif escolha == "u":
                self._atualizar_equipamento(equip)
                return
            elif escolha == "d":
                self.repo.deletar_equipamento(equip)
                print("Deletado com sucesso, voltando à seleção de dispositivo")
                return
            else:
                print("Essa opção não existe")

    def _atualizar_equipamento(self, equip):
        novo_hostname = input("\nInsira o novo hostname do dispositivo: ")
        novo_responsavel = input("Insira o novo responsável pelo dispositivo: ")
        novo_setor = input("Insira o novo setor onde o dispositivo está localizado: ")

        nova_opcao_tipo = self._ler_inteiro("Insira o novo tipo de dispositivo (número): ")
        if nova_opcao_tipo is None or nova_opcao_tipo not in (1, 2, 3, 4):
            print("Tipo inválido, mantendo o tipo atual")
            nova_opcao_tipo = None
        elif FabricaEquipamento.nome_do_tipo(nova_opcao_tipo) != equip.tipo():
            print("OBS: o tipo do dispositivo foi alterado; após a operação, "
                  "volte à seleção de dispositivo para escolher o novo tipo")

        self.repo.atualizar_equipamento(
            equip, novo_hostname, novo_responsavel, novo_setor, nova_opcao_tipo
        )
        print("Dados atualizados com sucesso")
        self._perguntar_atualizar_vulnerabilidade()

    def _perguntar_atualizar_vulnerabilidade(self):
        while True:
            escolha = input(
                "\nDeseja atualizar alguma vulnerabilidade também? (y/n):\n"
            ).strip().lower()
            if escolha == "n":
                return
            elif escolha == "y":
                id_vuln = self._ler_inteiro(
                    "\nInsira o VulnID da vulnerabilidade que deseja alterar:\n"
                )
                if id_vuln is None:
                    continue
                equip = self.repo.buscar_equipamento_da_vulnerabilidade(id_vuln)
                if equip is None:
                    print("VulnID não existe, retornando")
                    continue
                vuln = equip.buscar_vulnerabilidade(id_vuln)
                nova_descricao = input("\nInsira a nova descrição da vulnerabilidade: ")
                nova_categoria = input("Insira a nova categoria da vulnerabilidade: ")
                nova_severidade = input("Insira a nova severidade da vulnerabilidade: ")
                novo_status = input("Insira o novo status da vulnerabilidade: ")
                self.repo.atualizar_vulnerabilidade(
                    vuln, nova_descricao, nova_categoria, nova_severidade, novo_status
                )
                print("Vulnerabilidade atualizada com sucesso")
                return
            else:
                print("Opção inválida")

    def _menu_cadastrar(self):
        while True:
            print("""
Qual tipo de dispositivo você deseja cadastrar:
Pressione "1" para Laptop
Pressione "2" para Servidor
Pressione "3" para Roteador
Pressione "4" para Impressora
Pressione "5" para voltar
            """)
            opcao = self._ler_inteiro("")
            if opcao is None:
                continue
            if opcao == 5:
                return
            if opcao not in (1, 2, 3, 4):
                print("Essa opção não existe")
                continue
            self._menu_inserir(opcao)

    def _menu_inserir(self, opcao_tipo):
        while True:
            print("""
O que você gostaria de inserir:
Pressione "d" para novo dispositivo
Pressione "v" para nova vulnerabilidade
Pressione "r" para voltar
            """)
            escolha = input().strip().lower()

            if escolha == "r":
                return
            elif escolha == "d":
                self._cadastrar_dispositivo(opcao_tipo)
            elif escolha == "v":
                self._cadastrar_vulnerabilidade_por_id()
            else:
                print("Essa opção não existe")

    def _cadastrar_dispositivo(self, opcao_tipo):
        hostname = input("\nInsira o hostname do dispositivo: ")
        responsavel = input("Insira quem é o responsável pelo dispositivo: ")
        setor = input("Insira o setor onde o dispositivo está localizado: ")

        equip = self.repo.criar_equipamento(opcao_tipo, hostname, responsavel, setor)
        print(f"Dispositivo cadastrado com sucesso, ID: {equip.id}")

        while True:
            escolha = input(
                "\nO dispositivo possui alguma vulnerabilidade a ser inserida? (y/n)\n"
            ).strip().lower()
            if escolha == "n":
                return
            elif escolha == "y":
                self._inserir_vulnerabilidade(equip)
            else:
                print("Essa opção não existe")

    def _cadastrar_vulnerabilidade_por_id(self):
        id_equip = self._ler_inteiro(
            "\nInsira o ID do dispositivo para adicionar uma vulnerabilidade ou '0' para sair:\n"
        )
        if id_equip is None or id_equip == 0:
            return

        equip = self.repo.buscar_por_id(id_equip)
        if equip is None:
            print("ID não existe, retornando")
            return

        self._inserir_vulnerabilidade(equip)

    def _inserir_vulnerabilidade(self, equip):
        descricao = input("\nInsira a descrição da vulnerabilidade: ")
        categoria = input("Insira a categoria da vulnerabilidade: ")
        severidade = input("Insira a severidade da vulnerabilidade: ")
        status = input("Insira o status da vulnerabilidade: ")

        vuln = self.repo.adicionar_vulnerabilidade(equip, descricao, categoria, severidade, status)
        print(f"Vulnerabilidade cadastrada com sucesso, VulnID: {vuln.id}")


if __name__ == "__main__":
    repositorio = RepositorioJSON("dados.json")
    app = InterfaceConsole(repositorio)
    app.iniciar()