import sqlite3
from typing import List, Tuple

class HistoricoRepository:
    def __init__(self, conexao: sqlite3.Connection):
        self.conn = conexao

    def listar_historico_completo(self) -> List[Tuple]:
        # OTIMIZAÇÃO: Execução direta (o próprio objeto Connection funciona como atalho para o cursor)
        return self.conn.execute('''
            SELECT h.id_log, m.nome, h.data_hora, h.acao, h.detalhes 
            FROM historico_movimentacoes h
            LEFT JOIN monitor m ON h.id_monitor = m.id_monitor
            ORDER BY h.id_log DESC
        ''').fetchall()