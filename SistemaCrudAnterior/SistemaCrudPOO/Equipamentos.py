
from abc import ABC, abstractmethod


class Equipamento(ABC):

    def __init__(self, id_equipamento, nome, fabricante, modelo, endereco_ip, data_cadastro):
        self.id = id_equipamento
        self.nome = nome
        self.fabricante = fabricante
        self.modelo = modelo
        self.endereco_ip = endereco_ip
        self.data_cadastro = data_cadastro

    @abstractmethod
    def tipo(self):
       

    @classmethod
    @abstractmethod
    def from_dict(cls, dados):
        
    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo(),
            "nome": self.nome,
            "fabricante": self.fabricante,
            "modelo": self.modelo,
            "endereco_ip": self.endereco_ip,
            "data_cadastro": self.data_cadastro,
        }

    def __str__(self):
        return f"[{self.id}] {self.tipo()} - {self.nome} ({self.endereco_ip})"


class Servidor(Equipamento):

    def __init__(self, id_equipamento, nome, fabricante, modelo, endereco_ip,
                 data_cadastro, sistema_operacional, funcao):
        super().__init__(id_equipamento, nome, fabricante, modelo, endereco_ip, data_cadastro)
        self.sistema_operacional = sistema_operacional
        self.funcao = funcao

    def tipo(self):
        return "Servidor"

    def to_dict(self):
        dados = super().to_dict()
        dados["sistema_operacional"] = self.sistema_operacional
        dados["funcao"] = self.funcao
        return dados

    @classmethod
    def from_dict(cls, dados):
        return cls(
            id_equipamento=dados["id"],
            nome=dados["nome"],
            fabricante=dados["fabricante"],
            modelo=dados["modelo"],
            endereco_ip=dados["endereco_ip"],
            data_cadastro=dados["data_cadastro"],
            sistema_operacional=dados["sistema_operacional"],
            funcao=dados["funcao"],
        )


class EstacaoTrabalho(Equipamento):

    def __init__(self, id_equipamento, nome, fabricante, modelo, endereco_ip,
                 data_cadastro, usuario_responsavel, sistema_operacional):
        super().__init__(id_equipamento, nome, fabricante, modelo, endereco_ip, data_cadastro)
        self.usuario_responsavel = usuario_responsavel
        self.sistema_operacional = sistema_operacional

    def tipo(self):
        return "Estacao de Trabalho"

    def to_dict(self):
        dados = super().to_dict()
        dados["usuario_responsavel"] = self.usuario_responsavel
        dados["sistema_operacional"] = self.sistema_operacional
        return dados

    @classmethod
    def from_dict(cls, dados):
        return cls(
            id_equipamento=dados["id"],
            nome=dados["nome"],
            fabricante=dados["fabricante"],
            modelo=dados["modelo"],
            endereco_ip=dados["endereco_ip"],
            data_cadastro=dados["data_cadastro"],
            usuario_responsavel=dados["usuario_responsavel"],
            sistema_operacional=dados["sistema_operacional"],
        )


class Roteador(Equipamento):

    def __init__(self, id_equipamento, nome, fabricante, modelo, endereco_ip,
                 data_cadastro, numero_portas, suporta_vpn):
        super().__init__(id_equipamento, nome, fabricante, modelo, endereco_ip, data_cadastro)
        self.numero_portas = numero_portas
        self.suporta_vpn = suporta_vpn

    def tipo(self):
        return "Roteador"

    def to_dict(self):
        dados = super().to_dict()
        dados["numero_portas"] = self.numero_portas
        dados["suporta_vpn"] = self.suporta_vpn
        return dados

    @classmethod
    def from_dict(cls, dados):
        return cls(
            id_equipamento=dados["id"],
            nome=dados["nome"],
            fabricante=dados["fabricante"],
            modelo=dados["modelo"],
            endereco_ip=dados["endereco_ip"],
            data_cadastro=dados["data_cadastro"],
            numero_portas=dados["numero_portas"],
            suporta_vpn=dados["suporta_vpn"],
        )


class Firewall(Equipamento):

    def __init__(self, id_equipamento, nome, fabricante, modelo, endereco_ip,
                 data_cadastro, politica_padrao, numero_regras):
        super().__init__(id_equipamento, nome, fabricante, modelo, endereco_ip, data_cadastro)
        self.politica_padrao = politica_padrao
        self.numero_regras = numero_regras

    def tipo(self):
        return "Firewall"

    def to_dict(self):
        dados = super().to_dict()
        dados["politica_padrao"] = self.politica_padrao
        dados["numero_regras"] = self.numero_regras
        return dados

    @classmethod
    def from_dict(cls, dados):
        return cls(
            id_equipamento=dados["id"],
            nome=dados["nome"],
            fabricante=dados["fabricante"],
            modelo=dados["modelo"],
            endereco_ip=dados["endereco_ip"],
            data_cadastro=dados["data_cadastro"],
            politica_padrao=dados["politica_padrao"],
            numero_regras=dados["numero_regras"],
        )

TIPOS_EQUIPAMENTO = {
    "Servidor": Servidor,
    "Estacao de Trabalho": EstacaoTrabalho,
    "Roteador": Roteador,
    "Firewall": Firewall,
}

def criar_equipamento_a_partir_de_dict(dados):
   
    tipo = dados.get("tipo")
    classe = TIPOS_EQUIPAMENTO.get(tipo)
    if classe is None:
        raise ValueError(f"Tipo de equipamento desconhecido: {tipo}")
    return classe.from_dict(dados)