from enum import Enum


class TipoAtivo(Enum):
    NOTEBOOK = 1
    SERVIDOR = 2
    ROTEADOR = 3
    SOFTWARE_LICENCIADO = 4
    APLICACAO_WEB = 5
    BANCO_DE_DADOS = 6
    IMPRESSORA_REDE = 7
    ESTACAO_TRABALHO = 8


class Ativo:
    def __init__(self, id: int, nome: str, responsável: str, setor: str, tipo: TipoAtivo, descrição: str = ""):
        self.id = id
        self.nome = nome
        self.responsável = responsável
        self.setor = setor
        self.tipo = tipo
        self.descrição = descrição
        self.vulnerabilidades = []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "responsável": self.responsável,
            "setor": self.setor,
            "tipo": self.tipo.name,
            "descrição": self.descrição,
            "vulnerabilidades": [v.to_dict() for v in self.vulnerabilidades]
        }

    def exibir(self):
        linha = "=" * 50
        print(f"\n{linha}")
        print(f"  ATIVO #{self.id}")
        print(linha)
        print(f"  Nome/Hostname : {self.nome}")
        print(f"  Responsável   : {self.responsável}")
        print(f"  Setor         : {self.setor}")
        print(f"  Tipo          : {self.tipo.name.replace('_', ' ')}")
        print(f"  Descrição     : {self.descrição or 'Não informada'}")
        print(f"  Vulnerab.     : {len(self.vulnerabilidades)} registrada(s)")
        print(linha)
