import sqlite3
from typing import List
from modelos import Monitor

class MonitorRepository:
    def __init__(self, conexao: sqlite3.Connection):
        self.conn = conexao

    def listar_ativos(self) -> List[Monitor]:
        return [
            Monitor(id_monitor=row[0], nome=row[1], ativo=bool(row[2])) 
            for row in self.conn.execute("SELECT id_monitor, nome, ativo FROM monitor WHERE ativo = 1")
        ]

    def criar(self, nome: str) -> None:
        self.conn.execute("INSERT INTO monitor (nome) VALUES (?)", (nome,))

    def atualizar(self, id_monitor: int, novo_nome: str) -> None:
        self.conn.execute(
            "UPDATE monitor SET nome = ? WHERE id_monitor = ?", 
            (novo_nome, id_monitor)
        )

    def deletar(self, id_monitor: int) -> None:
        self.conn.execute(
            "UPDATE monitor SET ativo = 0 WHERE id_monitor = ?", 
            (id_monitor,)
        )