import matplotlib
matplotlib.use('Agg') 
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
from pathlib import Path
from config import PASTA_GRAFICOS

# @rodar_em_background  <-- Descomente quando criar o utilidades.py
def criar_grafico(dados_grafico, monitor_responsavel, data_hora, caminho_txt):
    if not dados_grafico:
        return None

    # OTIMIZAÇÃO: Desempacotamento limpo de dados O(N) sem percorrer listas múltiplas vezes
    materiais, esperado, encontrado, anotacoes_grafico = zip(*(
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
    
    labels_personalizados = [f"{enc}{anot}" for enc, anot in zip(encontrado, anotacoes_grafico)]
    ax.bar_label(barras_enc, labels=labels_personalizados, padding=8, color='#2c3e50', fontweight='bold', fontsize=13)
    
    ax.margins(x=0.25)
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    # OTIMIZAÇÃO: Uso nativo da pathlib em vez de os.path
    PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)
    
    caminho_txt_path = Path(caminho_txt)
    nome_imagem = PASTA_GRAFICOS / caminho_txt_path.name.replace('.txt', '.png')
    
    # Salvando e liberando a memória RAM para evitar vazamentos (Memory Leaks)
    fig.savefig(nome_imagem, dpi=300, bbox_inches='tight')
    fig.clf() 
    
    print(f"Sucesso! Gráfico salvo na Área de Trabalho em: {nome_imagem}")
    
    return str(nome_imagem)