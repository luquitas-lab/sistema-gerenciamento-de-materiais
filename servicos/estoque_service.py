from datetime import datetime
from repositorios.material_repository import MaterialRepository
from repositorios.monitor_repository import MonitorRepository
from excecoes import EstoqueInsuficienteError, MaterialNaoEncontradoError

class EstoqueService:
    def __init__(self, gerenciador_conexao):
        self.db = gerenciador_conexao

    def _obter_data_hora_atual(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def listar_materiais_ativos(self):
        with self.db.obter_conexao() as conn:
            return MaterialRepository(conn).listar_ativos()

    def criar_material(self, nome: str, quantidade: int, observacoes: str, id_monitor: int):
        with self.db.obter_conexao() as conn:
            with conn: 
                repo = MaterialRepository(conn)
                repo.criar_material(nome, quantidade, observacoes)
                repo.registrar_log(id_monitor, self._obter_data_hora_atual(), "CRIACAO_MATERIAL", f"Criado: {nome} (Qtd: {quantidade})")

    def atualizar_material(self, id_material: int, novo_nome: str, novas_obs: str, id_monitor: int):
        with self.db.obter_conexao() as conn:
            with conn: 
                repo = MaterialRepository(conn)
                repo.atualizar_material(id_material, novo_nome, novas_obs)
                repo.registrar_log(id_monitor, self._obter_data_hora_atual(), "ATUALIZACAO_MANUAL", f"Atualizado material ID {id_material}")

    def deletar_material(self, id_material: int, id_monitor: int):
        with self.db.obter_conexao() as conn:
            with conn: 
                repo = MaterialRepository(conn)
                repo.deletar_material(id_material)
                repo.registrar_log(id_monitor, self._obter_data_hora_atual(), "MATERIAL_ELIMINADO", f"Material ID {id_material} foi desativado.")

    def criar_monitor(self, nome: str) -> None:
        with self.db.obter_conexao() as conn:
            with conn: 
                MonitorRepository(conn).criar(nome)

    def atualizar_monitor(self, id_monitor: int, novo_nome: str) -> None:
        with self.db.obter_conexao() as conn:
            with conn:
                MonitorRepository(conn).atualizar(id_monitor, novo_nome)

    def deletar_monitor(self, id_monitor: int) -> None:
        with self.db.obter_conexao() as conn:
            with conn:
                MonitorRepository(conn).deletar(id_monitor)

    def listar_monitores_ativos(self):
        with self.db.obter_conexao() as conn:
            return MonitorRepository(conn).listar_ativos()

    def registrar_entrada_material(self, id_material: int, quantidade_adicionada: int, id_monitor: int, data_entrada: str) -> None:
        if quantidade_adicionada <= 0:
            raise ValueError("A quantidade da entrada deve ser maior que zero.")

        with self.db.obter_conexao() as conn:
            repo = MaterialRepository(conn)
            with conn: 
                material = repo.buscar_por_id(id_material)
                if not material:
                    raise MaterialNaoEncontradoError(f"O material ID {id_material} não foi encontrado.")
                
                nova_quantidade = material["quantidade"] + quantidade_adicionada
                repo.registrar_entrada(data_entrada, quantidade_adicionada, id_material)
                repo.atualizar_quantidade(id_material, nova_quantidade)
                repo.registrar_log(id_monitor, self._obter_data_hora_atual(), "ENTRADA", f"Adicionado {quantidade_adicionada} unidades ao material ID {id_material}")

    def registrar_baixa_por_dano(self, id_material: int, quantidade_perdida: int, id_monitor: int, data_baixa: str) -> None:
        if quantidade_perdida <= 0:
            raise ValueError("A quantidade da baixa deve ser maior que zero.")

        with self.db.obter_conexao() as conn:
            repo = MaterialRepository(conn)
            with conn:
                material = repo.buscar_por_id(id_material)
                if not material:
                    raise MaterialNaoEncontradoError(f"O material ID {id_material} não foi encontrado.")
                
                nova_quantidade = material["quantidade"] - quantidade_perdida
                if nova_quantidade < 0:
                    raise EstoqueInsuficienteError(f"Estoque insuficiente! Disponível: {material['quantidade']}")
                
                repo.registrar_dano(data_baixa, quantidade_perdida, id_material)
                repo.atualizar_quantidade(id_material, nova_quantidade)
                repo.registrar_log(id_monitor, self._obter_data_hora_atual(), "DANO_PERDA", f"Baixa de {quantidade_perdida} unidades do material ID {id_material}")