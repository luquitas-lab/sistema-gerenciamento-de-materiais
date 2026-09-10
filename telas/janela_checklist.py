import customtkinter as ctk
from tkinter import messagebox
import os
import platform
import subprocess

from modelos import ItemChecklist
from utils.executor import rodar_em_background

class JanelaChecklist(ctk.CTkToplevel):
    def __init__(self, master, servicos):
        super().__init__(master)
        
        self.servico_estoque = servicos["estoque"]
        self.servico_checklist = servicos["checklist"]
        
        self.title("Check-list Diário")
        self._configurar_geometria_responsiva()
        
        self.transient(master)
        self.grab_set()
        
        self.entradas_checklist = {}
        self.lista_entries = []

        ctk.CTkLabel(self, text="📝 Check-list de Materiais", font=("Segoe UI", 22, "bold"), text_color="#e0e0e0").pack(pady=(15, 5))

        if not self._configurar_monitor_responsavel():
            return

        self._configurar_cabecalho()
        self._configurar_lista()
        self._carregar_materiais()

        self.btn_salvar = ctk.CTkButton(self, text="Salvar e Registrar Check-list", command=self.iniciar_salvamento, 
                                        fg_color="#d35400", hover_color="#e67e22", text_color="white",
                                        font=("Segoe UI", 14, "bold"), height=40, corner_radius=8)
        self.btn_salvar.pack(pady=10)

    def _configurar_geometria_responsiva(self):
        largura_janela = 950
        altura_janela = 650
        
        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()
        
        largura_janela = min(largura_janela, largura_tela - 50)
        altura_janela = min(altura_janela, altura_tela - 80)
            
        pos_x = max(0, (largura_tela - largura_janela) // 2)
        pos_y = max(30, (altura_tela - altura_janela) // 5)
        
        self.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

    def _configurar_monitor_responsavel(self):
        try:
            monitores = self.servico_estoque.listar_monitores_ativos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar monitores: {e}", parent=self)
            self.destroy()
            return False

        if not monitores:
            messagebox.showwarning("Aviso", "Cadastre pelo menos um monitor antes!", parent=self)
            self.destroy()
            return False

        lista_monitores = [f"{m.id_monitor} - {m.nome}" for m in monitores]
        
        frame_monitor = ctk.CTkFrame(self, fg_color="transparent")
        frame_monitor.pack(pady=2)
        
        ctk.CTkLabel(frame_monitor, text="Monitor Responsável:", font=("Segoe UI", 12, "bold"), text_color="#e0e0e0").pack(side="left", padx=10)
        self.combo_monitor_resp = ctk.CTkComboBox(frame_monitor, values=lista_monitores, state="readonly", width=300)
        self.combo_monitor_resp.set(lista_monitores[0])
        self.combo_monitor_resp.pack(side="left", padx=5)
        return True

    def _configurar_cabecalho(self):
        self.frame_cabecalho = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=8)
        self.frame_cabecalho.pack(fill="x", padx=20, pady=(5, 0))
        
        font_cab = ("Segoe UI", 12, "bold")
        cor_cab = "#3498db"
        
        titulos = ["Material", "Esperado", "Encontrado", "Observação", "Quarto"]
        for i, texto in enumerate(titulos):
            sticky = "w" if i == 0 else ""
            ctk.CTkLabel(self.frame_cabecalho, text=texto, font=font_cab, text_color=cor_cab).grid(row=0, column=i, padx=10, pady=8, sticky=sticky)
        
        for i, t in enumerate([320, 90, 110, 140, 90]):
            self.frame_cabecalho.grid_columnconfigure(i, minsize=t)

    def _configurar_lista(self):
        self.frame_lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frame_lista.pack(fill="both", expand=True, padx=20, pady=(2, 2))

    def mover_foco(self, event, direcao, index):
        novo_index = index + direcao
        if 0 <= novo_index < len(self.lista_entries):
            self.lista_entries[novo_index].focus_set()
            try:
                self.frame_lista._parent_canvas.yview_moveto(novo_index / len(self.lista_entries))
            except Exception:
                pass
        return "break"

    def _carregar_materiais(self):
        try:
            materiais = self.servico_estoque.listar_materiais_ativos()
        except Exception as e:
            return messagebox.showerror("Erro", str(e), parent=self)
            
        if not materiais:
            return ctk.CTkLabel(self.frame_lista, text="Nenhum material cadastrado no sistema.", text_color="#e74c3c", font=("Segoe UI", 12)).pack(pady=20)

        for i, mat in enumerate(materiais):
            bg_color = "#2a2a2a" if i % 2 == 0 else "#1e1e1e"
            frame_linha = ctk.CTkFrame(self.frame_lista, fg_color=bg_color, corner_radius=6)
            frame_linha.pack(fill="x", pady=2, padx=5)

            ctk.CTkLabel(frame_linha, text=mat.nome, text_color="#e0e0e0").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(frame_linha, text=str(mat.quantidade), text_color="#e0e0e0").grid(row=0, column=1, padx=10, pady=5)

            entry_qtd = ctk.CTkEntry(frame_linha, width=70, justify="center")
            entry_qtd.grid(row=0, column=2, padx=10, pady=5)

            combo_obs = ctk.CTkComboBox(frame_linha, values=["", "Pendente", "Danificado"], state="readonly", width=120)
            combo_obs.set("")
            combo_obs.grid(row=0, column=3, padx=10, pady=5)

            entry_quarto = ctk.CTkEntry(frame_linha, width=70, justify="center")
            entry_quarto.grid(row=0, column=4, padx=10, pady=5)

            for col, t in enumerate([320, 90, 110, 140, 90]):
                frame_linha.grid_columnconfigure(col, minsize=t)

            self.entradas_checklist[mat.id_material] = (mat.nome, mat.quantidade, entry_qtd, combo_obs, entry_quarto)
            self.lista_entries.append(entry_qtd)

        for index, entry in enumerate(self.lista_entries):
            entry.bind("<Up>", lambda event, idx=index: self.mover_foco(event, -1, idx))
            entry.bind("<Down>", lambda event, idx=index: self.mover_foco(event, 1, idx))

        if self.lista_entries:
            self.lista_entries[0].focus_set()

    def iniciar_salvamento(self):
        if not self.entradas_checklist:
            return messagebox.showwarning("Aviso", "Não há materiais no check-list!", parent=self)
            
        monitor_responsavel = self.combo_monitor_resp.get().split(" - ", 1)[1]
        itens_verificados = []
        
        for id_mat, (nome, qtd_esperada, entry, combo_obs, entry_quarto) in self.entradas_checklist.items():
            qtd_txt = entry.get().strip()
            
            if not qtd_txt:
                return messagebox.showerror("Erro", f"Você esqueceu de preencher a quantidade de '{nome}'.", parent=self)
                
            try:
                qtd_encontrada = int(qtd_txt)
                if qtd_encontrada < 0: raise ValueError
            except ValueError:
                return messagebox.showerror("Erro", f"A quantidade de '{nome}' deve ser um número inteiro positivo!", parent=self)
                
            itens_verificados.append(
                ItemChecklist(
                    id_material=id_mat,
                    nome_material=nome,
                    qtd_esperada=qtd_esperada,
                    qtd_encontrada=qtd_encontrada,
                    observacao=combo_obs.get(),
                    quarto=entry_quarto.get().strip()
                )
            )

        self.btn_salvar.configure(state="disabled", text="Gerando Relatório... Aguarde!", fg_color="#555555")

        rodar_em_background(
            self, 
            self.servico_checklist.processar_checklist, 
            self.finalizar_salvamento, 
            lambda erro: self._restaurar_botao_erro(f"Falha na geração: {erro}"),
            monitor_responsavel=monitor_responsavel,
            itens=itens_verificados
        )
        
    def _restaurar_botao_erro(self, mensagem):
        messagebox.showerror("Erro Crítico", mensagem, parent=self)
        self.btn_salvar.configure(state="normal", text="Salvar e Registrar Check-list", fg_color="#d35400")

    def finalizar_salvamento(self, resultado):
        if not self.winfo_exists(): return
        
        if not resultado["sucesso"]:
            return self._restaurar_botao_erro(resultado.get("erro", "Erro desconhecido"))
        
        try:
            caminho_imagem = resultado["nome_imagem"]
            sistema_os = platform.system()
            if sistema_os == "Windows": os.startfile(caminho_imagem)
            elif sistema_os == "Darwin": subprocess.Popen(["open", caminho_imagem])
            else: subprocess.Popen(["xdg-open", caminho_imagem])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir a imagem: {e}", parent=self)

        if resultado["alertas"]:
            mensagem_final = "Check-list pronto!\n\nAlertas:\n\n" + "\n".join(resultado["alertas"])
            messagebox.showwarning("Atenção!", mensagem_final, parent=self)
        else:
            messagebox.showinfo("Sucesso", "Check-list perfeito! Nenhum item faltando.", parent=self)
            
        self.destroy()