import sqlite3
from typing import List, Optional
from modelos import Material

class MaterialRepository:
    def __init__(self, conexao: sqlite3.Connection):
        self.conn = conexao

    def listar_ativos(self) -> List[Material]:
        # OTIMIZAÇÃO: List comprehension iterando diretamente sobre o retorno do banco
        return [
            Material(
                id_material=linha[0],
                nome=linha[1],
                quantidade=linha[2],
                observacoes=linha[3],
                ativo=bool(linha[4])
            )
            for linha in self.conn.execute(
                "SELECT id_material, nome, quantidade_material, observacoes, ativo FROM material WHERE ativo = 1"
            )
        ]

    def buscar_por_id(self, id_material: int) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT id_material, nome, quantidade_material FROM material WHERE id_material = ? AND ativo = 1", 
            (id_material,)
        ).fetchone()
        
        return {"id_material": row[0], "nome": row[1], "quantidade": row[2]} if row else None

    def criar_material(self, nome: str, quantidade: int, observacoes: str = "") -> int:
        return self.conn.execute(
            "INSERT INTO material (nome, quantidade_material, observacoes) VALUES (?, ?, ?)",
            (nome, quantidade, observacoes)
        ).lastrowid

    def atualizar_material(self, id_material: int, novo_nome: str, novas_obs: str) -> None:
        self.conn.execute(
            "UPDATE material SET nome = ?, observacoes = ? WHERE id_material = ?",
            (novo_nome, novas_obs, id_material)
        )

    def deletar_material(self, id_material: int) -> None:
        self.conn.execute(
            "UPDATE material SET ativo = 0 WHERE id_material = ?",
            (id_material,)
        )

    def atualizar_quantidade(self, id_material: int, nova_quantidade: int) -> None:
        self.conn.execute(
            "UPDATE material SET quantidade_material = ? WHERE id_material = ?",
            (nova_quantidade, id_material)
        )

    def registrar_entrada(self, data_entrada: str, quantidade: int, id_material: int) -> None:
        self.conn.execute(
            "INSERT INTO entrada (entrada, quantidade_entrada, id_material) VALUES (?, ?, ?)",
            (data_entrada, quantidade, id_material)
        )

    def registrar_dano(self, data_danos: str, quantidade: int, id_material: int) -> None:
        self.conn.execute(
            "INSERT INTO danos (data_danos, quantidade_danos, id_material) VALUES (?, ?, ?)",
            (data_danos, quantidade, id_material)
        )

    def registrar_log(self, id_monitor: int, data_hora: str, acao: str, detalhes: str) -> None:
        self.conn.execute(
            "INSERT INTO historico_movimentacoes (id_monitor, data_hora, acao, detalhes) VALUES (?, ?, ?, ?)",
            (id_monitor, data_hora, acao, detalhes)
        )