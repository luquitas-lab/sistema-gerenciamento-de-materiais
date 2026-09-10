import customtkinter as ctk
from tkinter import messagebox

class JanelaMonitor(ctk.CTkToplevel):
    def __init__(self, master, servico_estoque):
        super().__init__(master)
        self.servico_estoque = servico_estoque
        self.title("Gerenciar Monitores")
        self.geometry("450x400")
        self.transient(master)
        self.grab_set()
        
        self._cache_monitores = {}
        
        self.abas = ctk.CTkTabview(self, corner_radius=10, fg_color="#1e1e1e")
        self.abas.pack(fill="both", expand=True, padx=20, pady=20)

        for aba in [" Cadastrar ", " Atualizar ", " Deletar "]:
            self.abas.add(aba)

        self.aba_cadastrar = self.abas.tab(" Cadastrar ")
        self.aba_atualizar = self.abas.tab(" Atualizar ")
        self.aba_deletar = self.abas.tab(" Deletar ")

        self._construir_aba_cadastrar()
        self._construir_aba_atualizar()
        self._construir_aba_deletar()
        self.atualizar_listas()

    def _construir_aba_cadastrar(self):
        ctk.CTkLabel(self.aba_cadastrar, text="Cadastrar Novo Monitor", font=("Segoe UI", 18, "bold"), text_color="#e0e0e0").pack(pady=(25, 15))
        
        ctk.CTkLabel(self.aba_cadastrar, text="Nome Completo do Monitor:", text_color="#a0a0a0").pack(anchor="w", padx=40, pady=(10, 0))
        self.entry_nome_mon = ctk.CTkEntry(self.aba_cadastrar, width=320, height=35)
        self.entry_nome_mon.pack(pady=5)
        
        ctk.CTkButton(self.aba_cadastrar, text="Salvar Monitor", command=self.salvar_monitor, 
                      fg_color="#27ae60", hover_color="#2ecc71", font=("Segoe UI", 12, "bold"), height=40).pack(pady=30)

    def _construir_aba_atualizar(self):
        ctk.CTkLabel(self.aba_atualizar, text="Atualizar Monitor", font=("Segoe UI", 18, "bold"), text_color="#e0e0e0").pack(pady=(25, 15))
        
        ctk.CTkLabel(self.aba_atualizar, text="Selecione o Monitor antigo:", text_color="#a0a0a0").pack(anchor="w", padx=40, pady=(5, 0))
        self.combo_atualizar = ctk.CTkComboBox(self.aba_atualizar, state="readonly", width=320, height=35, command=self.preencher_dados_atuais)
        self.combo_atualizar.pack(pady=5)
        
        ctk.CTkLabel(self.aba_atualizar, text="Digite o Novo Nome:", text_color="#a0a0a0").pack(anchor="w", padx=40, pady=(10, 0))
        self.entry_novo_nome = ctk.CTkEntry(self.aba_atualizar, width=320, height=35)
        self.entry_novo_nome.pack(pady=5)
        
        ctk.CTkButton(self.aba_atualizar, text="Atualizar Nome", command=self.btn_atualizar_click, 
                      fg_color="#2980b9", hover_color="#3498db", font=("Segoe UI", 12, "bold"), height=40).pack(pady=25)

    def _construir_aba_deletar(self):
        ctk.CTkLabel(self.aba_deletar, text="Deletar Monitor", font=("Segoe UI", 18, "bold"), text_color="#e74c3c").pack(pady=(35, 15))
        
        ctk.CTkLabel(self.aba_deletar, text="Selecione o Monitor a ser removido:", text_color="#a0a0a0").pack(anchor="w", padx=40, pady=(10, 0))
        self.combo_deletar = ctk.CTkComboBox(self.aba_deletar, state="readonly", width=320, height=35)
        self.combo_deletar.pack(pady=5)
        
        ctk.CTkButton(self.aba_deletar, text="🗑️ Deletar Monitor", command=self.btn_deletar_click, 
                      fg_color="#c0392b", hover_color="#e74c3c", font=("Segoe UI", 12, "bold"), height=40).pack(pady=35)

    def preencher_dados_atuais(self, valor_selecionado=None):
        selecionado = self.combo_atualizar.get()
        if not selecionado: return
        
        id_mon = int(selecionado.split(" - ")[0])
        monitor = self._cache_monitores.get(id_mon)
        
        if monitor:
            self.entry_novo_nome.delete(0, 'end')
            self.entry_novo_nome.insert(0, monitor.nome)

    def atualizar_listas(self):
        sel_atual = self.combo_atualizar.get()
        try:
            monitores = self.servico_estoque.listar_monitores_ativos()
            self._cache_monitores = {m.id_monitor: m for m in monitores}
            lista_formatada = [f"{m.id_monitor} - {m.nome}" for m in monitores]
            
            if lista_formatada:
                self.combo_atualizar.configure(values=lista_formatada)
                self.combo_deletar.configure(values=lista_formatada)
                
                self.combo_atualizar.set(sel_atual if sel_atual in lista_formatada else lista_formatada[0])
                self.combo_deletar.set(lista_formatada[0])
                self.preencher_dados_atuais()
            else:
                for combo in (self.combo_atualizar, self.combo_deletar):
                    combo.configure(values=[""])
                    combo.set("")
                self.entry_novo_nome.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar listas: {e}", parent=self)

    def salvar_monitor(self):
        nome = self.entry_nome_mon.get().strip()
        if not nome: return messagebox.showerror("Erro", "O nome é obrigatório!", parent=self)
            
        try:
            self.servico_estoque.criar_monitor(nome)
            messagebox.showinfo("Sucesso", f"Monitor '{nome}' cadastrado!", parent=self)
            self.entry_nome_mon.delete(0, 'end')
            self.atualizar_listas() 
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}", parent=self)

    def btn_atualizar_click(self):
        selecionado = self.combo_atualizar.get()
        novo_nome = self.entry_novo_nome.get().strip()
        
        if not selecionado or not novo_nome: 
            return messagebox.showerror("Erro", "Selecione o monitor e preencha o novo nome!", parent=self)
            
        try:
            id_monitor = int(selecionado.split(" - ")[0])
            self.servico_estoque.atualizar_monitor(id_monitor, novo_nome)
            messagebox.showinfo("Sucesso", "Monitor atualizado com sucesso!", parent=self)
            self.entry_novo_nome.delete(0, 'end')
            self.atualizar_listas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar: {e}", parent=self)

    def btn_deletar_click(self):
        selecionado = self.combo_deletar.get()
        if not selecionado: 
            return messagebox.showerror("Erro", "Selecione um monitor para deletar!", parent=self)
            
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar:\n{selecionado}?", parent=self):
            try:
                id_monitor = int(selecionado.split(" - ")[0])
                self.servico_estoque.deletar_monitor(id_monitor)
                messagebox.showinfo("Sucesso", "Monitor deletado com sucesso!", parent=self)
                self.atualizar_listas()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao deletar: {e}", parent=self)