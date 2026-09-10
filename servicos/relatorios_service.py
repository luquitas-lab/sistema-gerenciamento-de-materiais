import matplotlib
matplotlib.use('Agg') 
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
from repositorios.historico_repository import HistoricoRepository
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from config import PASTA_RELATORIOS, PASTA_GRAFICOS

class RelatorioService:
    def __init__(self, gerenciador_conexao=None):
        self.db = gerenciador_conexao

    def listar_historico(self):
        if not self.db: return []
        with self.db.obter_conexao() as conn:
            return HistoricoRepository(conn).listar_historico_completo()

    def gerar_relatorio_inventario(self, nome_responsavel: str, materiais: List[Dict[str, Any]]) -> Path:
        agora = datetime.now()
        agora_formatada = agora.strftime("%d/%m/%Y às %H:%M:%S")
        nome_arquivo = f"Relatorio_Inventario_{agora.strftime('%Y-%m-%d_%H%M%S')}.txt"
        
        PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)
        caminho_arquivo = PASTA_RELATORIOS / nome_arquivo
        
        linhas = [
            "=" * 70 + "\n     RELATÓRIO OFICIAL DE INVENTÁRIO\n" + "=" * 70 + "\n",
            f"Gerado em: {agora_formatada}\n\n--- POSIÇÃO ATUAL DO ESTOQUE ---\n\n"
        ]
        
        if not materiais:
            linhas.append("Nenhum material cadastrado no sistema.\n")
        else:
            linhas.extend([
                f"{'ID':<5} | {'NOME DO MATERIAL':<25} | {'QTD':<5} | {'OBSERVAÇÕES'}\n",
                "-" * 70 + "\n"
            ])
            for mat in materiais:
                obs = mat.get('observacoes') or "Nenhuma"
                nome = mat.get('nome', '')
                nome_formatado = nome[:22] + "..." if len(nome) > 25 else nome
                linhas.append(f"{mat['id_material']:<5} | {nome_formatado:<25} | {mat['quantidade']:<5} | {obs}\n")
        
        linhas.append("\n" + "=" * 70 + f"\nRelatório gerado por: {nome_responsavel}\n" + "=" * 70 + "\n")
        
        # OTIMIZAÇÃO: Escrita em lote única
        with caminho_arquivo.open("w", encoding="utf-8") as arquivo:
            arquivo.writelines(linhas)
            
        return caminho_arquivo

    def gerar_grafico_checklist(self, dados_grafico: List[Dict[str, Any]], monitor_responsavel: str, data_hora: str, nome_base_txt: str) -> Path:
        if not dados_grafico:
            raise ValueError("Não há dados para gerar o gráfico.")

        # OTIMIZAÇÃO: Desempacotamento de dados e reversão da lista em O(N) de uma só vez
        materiais, esperado, encontrado, anotacoes = zip(*(
            (d['material'], d['esperado'], d['encontrado'], d['anotacao']) 
            for d in reversed(dados_grafico)
        ))

        altura_dinamica = max(10.0, len(materiais) * 0.6)
        fig = Figure(figsize=(16, altura_dinamica))
        fig.patch.set_facecolor('#f8f9fa')
        
        canvas = FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)
        ax.set_facecolor('#f8f9fa')
        
        y = np.arange(len(materiais))
        altura = 0.35

        cor_esperado = '#ced4da' 
        ax.barh(y + altura/2, esperado, altura, label='Esperado', color=cor_esperado, edgecolor='none')
        
        cores_encontrado = ['#e74c3c' if enc < esp else '#3498db' for enc, esp in zip(encontrado, esperado)]
        barras_enc = ax.barh(y - altura/2, encontrado, altura, label='Encontrado', color=cores_encontrado, edgecolor='none')

        ax.set_xlabel('Quantidade de Itens', fontsize=14, fontweight='bold', color='#34495e', labelpad=15)
        
        titulo_grafico = f'Relatório de Check-list Diário\nConferido por: {monitor_responsavel}'
        if data_hora:
            titulo_grafico += f'   |   {data_hora}'
            
        ax.set_title(titulo_grafico, fontsize=20, fontweight='bold', color='#2c3e50', pad=20)
        
        ax.set_yticks(y)
        ax.set_yticklabels(materiais, fontsize=13, color='#34495e')
        ax.tick_params(axis='x', labelsize=12, colors='#34495e')
        ax.tick_params(axis='y', length=0)
        
        ax.xaxis.grid(True, linestyle='--', alpha=0.5, color='#adb5bd')
        ax.set_axisbelow(True)

        for spine in ['top', 'right', 'left']:
            ax.spines[spine].set_visible(False)
        ax.spines['bottom'].set_color('#adb5bd')
        ax.spines['bottom'].set_linewidth(1)

        ax.legend(fontsize=13, loc='upper right', frameon=True, facecolor='white', edgecolor='#e9ecef', framealpha=0.9)
        
        labels_personalizados = [f"{enc}{anot}" for enc, anot in zip(encontrado, anotacoes)]
        ax.bar_label(barras_enc, labels=labels_personalizados, padding=8, color='#2c3e50', fontweight='bold', fontsize=13)
        ax.margins(x=0.25)
        fig.tight_layout(rect=[0, 0, 1, 0.95])

        PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)
        nome_imagem = nome_base_txt.replace('.txt', '.png')
        caminho_imagem = PASTA_GRAFICOS / nome_imagem
        
        fig.savefig(caminho_imagem, dpi=300, bbox_inches='tight')
        
        return caminho_imagem