from datetime import datetime
from typing import List, Dict, Any
from modelos import ItemChecklist
from config import PASTA_RELATORIOS
from servicos.relatorios_service import RelatorioService

class ChecklistService:
    def __init__(self, gerenciador_conexao):
        self.db = gerenciador_conexao
        self.relatorio_service = RelatorioService()

    def processar_checklist(self, monitor_responsavel: str, itens: List[ItemChecklist]) -> Dict[str, Any]:
        agora_completo = datetime.now()
        agora_str = agora_completo.strftime("%d/%m/%Y às %H:%M:%S")

        alertas = []
        detalhes_relatorio = []
        dados_grafico = [] 
        acoes_bd = []

        for item in itens:
            qtd_esperada = item.qtd_esperada
            qtd_encontrada = item.qtd_encontrada
            nome = item.nome_material
            obs_texto = item.observacao or "-"
            quarto_texto = item.quarto or "-"

            status_txt = "OK"
            info_extra = []
            texto_anotacao = "" 
            
            nome_formatado = nome[:32] + "..." if len(nome) > 35 else nome
            obs_lower = obs_texto.lower() if obs_texto != "-" else ""

            if obs_texto != "-":
                info_extra.append(f"Obs: {obs_texto}")
                if obs_lower in ['pendente', 'danificado']:
                    texto_anotacao = f"   [{nome_formatado} no Qto: {quarto_texto}]" if (quarto_texto and quarto_texto != '-') else f"   [{nome_formatado}]"
                    
            if quarto_texto != "-":
                info_extra.append(f"Qto: {quarto_texto}")

            aviso_extra = f" - ({' | '.join(info_extra)})" if info_extra else ""

            if qtd_encontrada < qtd_esperada:
                diferenca = qtd_esperada - qtd_encontrada
                alertas.append(f"⚠️ Faltam {diferenca}x '{nome}'{aviso_extra} (Anotado no relatório)")
                status_txt = f"FALTAM {diferenca}"
                acoes_bd.append({'tipo': 'falta', 'qtd': diferenca, 'id_mat': item.id_material}) 

            elif qtd_encontrada > qtd_esperada:
                sobra = qtd_encontrada - qtd_esperada
                alertas.append(f"❓ Sobram {sobra}x '{nome}'{aviso_extra} (Anotado no relatório)")
                status_txt = f"SOBRAM {sobra}"
                acoes_bd.append({'tipo': 'sobra', 'qtd': sobra, 'id_mat': item.id_material}) 
                
            elif obs_lower in ['pendente', 'danificado']:
                alertas.append(f"⚠️ Atenção: '{nome}' tem a quantidade certa, mas foi marcado como '{obs_texto}'{aviso_extra}")
                status_txt = f"ATENÇÃO: {obs_texto.upper()}"

            detalhes_relatorio.append(
                f"{nome_formatado:<35} | {qtd_esperada:<9} | {qtd_encontrada:<10} | {status_txt:<15} | {obs_texto:<12} | {quarto_texto}\n"
            )
            
            dados_grafico.append({
                'material': nome,
                'esperado': qtd_esperada,
                'encontrado': qtd_encontrada,
                'anotacao': texto_anotacao
            })

        PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)
        nome_base_txt = f"Checklist_{agora_completo.strftime('%Y-%m-%d_%H%M%S')}.txt"
        caminho_arquivo_txt = PASTA_RELATORIOS / nome_base_txt
        
        # OTIMIZAÇÃO: Gravando tudo na memória primeiro e escrevendo no disco de uma vez
        linhas_arquivo = [
            "=" * 105 + "\n",
            "                                RELATÓRIO DE CHECK-LIST DIÁRIO\n",
            "=" * 105 + "\n",
            f"Data e Hora da Conferência: {agora_str}\n",
            f"Conferido por (Monitor): {monitor_responsavel}\n\n",
            f"{'MATERIAL':<35} | {'ESPERADO':<9} | {'ENCONTRADO':<10} | {'STATUS':<15} | {'OBSERVAÇÃO':<12} | {'QUARTO'}\n",
            "-" * 105 + "\n"
        ]
        linhas_arquivo.extend(detalhes_relatorio)
        linhas_arquivo.extend([
            "\n" + "=" * 105 + "\n",
            "RESUMO DE DIVERGÊNCIAS E ANOTAÇÕES:\n"
        ])
        
        if alertas:
            linhas_arquivo.extend(f"{alerta}\n" for alerta in alertas)
        else:
            linhas_arquivo.append("Nenhuma divergência de quantidade encontrada. Estoque perfeito!\n")
            
        linhas_arquivo.append("=" * 105 + "\n")

        try:
            with caminho_arquivo_txt.open("w", encoding="utf-8") as arquivo:
                arquivo.writelines(linhas_arquivo)
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao gerar o arquivo txt: {e}"}

        try:
            caminho_imagem = self.relatorio_service.gerar_grafico_checklist(
                dados_grafico=dados_grafico, 
                monitor_responsavel=monitor_responsavel, 
                data_hora=agora_str, 
                nome_base_txt=nome_base_txt
            )
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao gerar o gráfico em PNG: {e}"}

        return {
            "sucesso": True,
            "alertas": alertas,
            "nome_arquivo_txt": str(caminho_arquivo_txt),
            "nome_imagem": str(caminho_imagem),
            "acoes_bd": acoes_bd  
        }