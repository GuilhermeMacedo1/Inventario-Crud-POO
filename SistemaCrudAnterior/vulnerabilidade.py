class Vulnerabilidade:
    SEVERIDADES = ["baixa", "media", "alta", "crítica"]
    STATUS_OPÇÕES = ["aberta", "em_tratamento", "corrigida", "aceita"]

    def __init__(self, descrição: str, categoria: str, severidade: str, status: str):
        self.descrição = descrição
        self.categoria = categoria
        self.severidade = severidade
        self.status = status

    def to_dict(self) -> dict:
        return {
            "descrição": self.descrição,
            "categoria": self.categoria,
            "severidade": self.severidade,
            "status": self.status
        }

    def exibir(self, numero: int):
        print(f"    [{numero}] {self.descrição}")
        print(f"        Categoria : {self.categoria}")
        print(f"        Severidade: {self.severidade.upper()}")
        print(f"        Status    : {self.status.replace('_', ' ')}")
