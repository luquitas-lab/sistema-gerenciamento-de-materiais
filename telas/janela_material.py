import customtkinter as ctk
from tkinter import messagebox

class JanelaMaterial(ctk.CTkToplevel):
    def __init__(self, master, servico_estoque):
        super().__init__(master)
        self.servico_estoque = servico_estoque
        self.title("Gerenciar Materiais")
        self.geometry("450x580") 
        self.transient(master)
        self.grab_set()

        self._cache_materiais = {}

        if not self._configurar_monitor_responsavel():
            return

        self.abas = ctk.CTkTabview(self, corner_radius=10, fg_color="#1e1e1e")
        self.abas.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        for aba in [" Cadastrar Novo ", " Atualizar ", " Deletar "]:
            self.abas.add(aba)

        self.aba_cadastrar = self.abas.tab(" Cadastrar Novo ")
        self.aba_atualizar = self.abas.tab(" Atualizar ")
        self.aba_deletar = self.abas.tab(" Deletar ")

        self._construir_aba_cadastrar()
        self._construir_aba_atualizar()
        self._construir_aba_deletar()
        self.atualizar_listas_mat()

    def _configurar_monitor_responsavel(self):
        try:
            monitores = self.servico_estoque.listar_monitores_ativos()
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self)
            self.destroy()
            return False

        if not monitores:
            messagebox.showwarning("Aviso", "Cadastre um monitor antes!", parent=self)
            self.destroy()
            return False

        lista_monitores = [f"{m.id_monitor} - {m.nome}" for m in monitores]
        frame_monitor = ctk.CTkFrame(self, fg_color="transparent")
        frame_monitor.pack(pady=(15, 10))
        
        ctk.CTkLabel(frame_monitor, text="Monitor:", font=("Segoe UI", 12, "bold"), text_color="#e0e0e0").pack(side="left", padx=10)
        self.combo_monitor_resp = ctk.CTkComboBox(frame_monitor, values=lista_monitores, state="readonly", width=250)
        self.combo_monitor_resp.set(lista_monitores[0])
        self.combo_monitor_resp.pack(side="left", padx=5)
        return True

    def _construir_aba_cadastrar(self):
        ctk.CTkLabel(self.aba_cadastrar, text="Cadastrar Novo Material", font=("Segoe UI", 18, "bold"), text_color="#e0e0e0").pack(pady=(15, 15))
        
        campos = [("Nome do Material (ex: Raquete):", "entry_nome"), 
                  ("Quantidade Inicial no Estoque:", "entry_quantidade"),
                  ("Observações (Marca, Cor, etc):", "entry_obs")]
                  
        for texto, attr in campos:
            ctk.CTkLabel(self.aba_cadastrar, text=texto, text_color="#a0a0a0").pack(anchor="w", padx=40, pady=(10 if attr != "entry_nome" else 5, 0))
            entry = ctk.CTkEntry(self.aba_cadastrar, width=320, height=35)
            entry.pack(pady=5)
            setattr(self, attr, entry)
            
        ctk.CTkButton(self.aba_cadastrar, text="Salvar Material", command=self.salvar_material, 
                      fg_color="#27ae60", hover_color="#2ecc71", font=("Segoe UI", 12, "bold"), height=40).pack(pady=25)

    def _construir_aba_atualizar(self):
        ctk.CTkLabel(self.aba_atualizar, text="Atualizar Material", font=("Segoe UI", 18, "bold"), text_color="#e0e0e0").pack(pady=(15, 15))
        
        ctk.CTkLabel(self.aba_atualizar, text="Selecione o Material antigo:", text_color="#a0a0a0").pack(anchor="w", padx=40, pady=(5, 0))
        self.combo_atualizar_mat = ctk.CTkComboBox(self.aba_atualizar, state="readonly", width=320, height=35, command=self.preencher_dados_atuais)
        self.combo_atualizar_mat.pack(pady=5)
        
        ctk.CTkLabel(self.aba_atualizar, text="Novo Nome:", text_color="#a0a0a0").pack(anchor="w", padx=40, pady=(10, 0))
        self.entry_novo_nome_mat = ctk.CTkEntry(self.aba_atualizar, width=320, height=35)
        self.entry_novo_nome_mat.pack(pady=5)
        
        ctk.CTkLabel(self.aba_atualizar, text="Novas Observações:", text_color="#a0a0a0").pack(anchor="w", padx=40, pady=(10, 0))
        self.entry_novas_obs = ctk.CTkEntry(self.aba_atualizar, width=320, height=35)
        self.entry_novas_obs.pack(pady=5)
        
        ctk.CTkButton(self.aba_atualizar, text="Atualizar Material", command=self.btn_atualizar_mat_click, 
                      fg_color="#2980b9", hover_color="#3498db", font=("Segoe UI", 12, "bold"), height=40).pack(pady=25)

    def _construir_aba_deletar(self):
        ctk.CTkLabel(self.aba_deletar, text="Deletar Material", font=("Segoe UI", 18, "bold"), text_color="#e74c3c").pack(pady=(35, 15))
        
        ctk.CTkLabel(self.aba_deletar, text="Selecione o Material a ser removido:", text_color="#a0a0a0").pack(anchor="w", padx=40, pady=(10, 0))
        self.combo_deletar_mat = ctk.CTkComboBox(self.aba_deletar, state="readonly", width=320, height=35)
        self.combo_deletar_mat.pack(pady=5)
        
        ctk.CTkButton(self.aba_deletar, text="🗑️ Deletar Material", command=self.btn_deletar_mat_click, 
                      fg_color="#c0392b", hover_color="#e74c3c", font=("Segoe UI", 12, "bold"), height=40).pack(pady=35)

    def preencher_dados_atuais(self, valor_selecionado=None):
        selecionado = self.combo_atualizar_mat.get()
        if not selecionado: return
        
        id_mat = int(selecionado.split(" - ")[0])
        
        material = self._cache_materiais.get(id_mat)
        
        if material:
            self.entry_novo_nome_mat.delete(0, 'end')
            self.entry_novo_nome_mat.insert(0, material.nome) 
            self.entry_novas_obs.delete(0, 'end')
            if material.observacoes: 
                self.entry_novas_obs.insert(0, material.observacoes)

    def atualizar_listas_mat(self):
        sel_atual = self.combo_atualizar_mat.get()
        sel_del = self.combo_deletar_mat.get()

        try:
            materiais = self.servico_estoque.listar_materiais_ativos()
            self._cache_materiais = {m.id_material: m for m in materiais}
            
            lista_formatada = [f"{m.id_material} - {m.nome}" for m in materiais]
            
            if lista_formatada:
                self.combo_atualizar_mat.configure(values=lista_formatada)
                self.combo_deletar_mat.configure(values=lista_formatada)
                
                self.combo_atualizar_mat.set(sel_atual if sel_atual in lista_formatada else lista_formatada[0])
                self.combo_deletar_mat.set(sel_del if sel_del in lista_formatada else lista_formatada[0])
                self.preencher_dados_atuais()
            else:
                self.combo_atualizar_mat.configure(values=[""])
                self.combo_deletar_mat.configure(values=[""])
                self.combo_atualizar_mat.set("")
                self.combo_deletar_mat.set("")
                self.entry_novo_nome_mat.delete(0, 'end')
                self.entry_novas_obs.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar listas: {e}", parent=self)

    def salvar_material(self):
        nome = self.entry_nome.get().strip()
        quantidade_texto = self.entry_quantidade.get()
        
        if not nome or not quantidade_texto:
            return messagebox.showerror("Erro", "Nome e quantidade são obrigatórios!", parent=self)
            
        nomes_existentes = [m.nome.lower() for m in self._cache_materiais.values()]
        if nome.lower() in nomes_existentes:
            return messagebox.showwarning("Aviso", f"Já existe material '{nome}'!", parent=self)

        try:
            quantidade = int(quantidade_texto)
            if quantidade < 0: return messagebox.showerror("Erro", "Quantidade negativa não permitida!", parent=self)
        except ValueError:
            return messagebox.showerror("Erro", "A quantidade deve ser um número inteiro!", parent=self)
            
        try:
            id_monitor = int(self.combo_monitor_resp.get().split(" - ")[0])
            self.servico_estoque.criar_material(nome, quantidade, self.entry_obs.get(), id_monitor=id_monitor)
            
            messagebox.showinfo("Sucesso", f"Material '{nome}' cadastrado!", parent=self)
            self.entry_nome.delete(0, 'end')
            self.entry_quantidade.delete(0, 'end')
            self.entry_obs.delete(0, 'end')
            self.atualizar_listas_mat() 
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}", parent=self)

    def btn_atualizar_mat_click(self):
        selecionado = self.combo_atualizar_mat.get()
        novo_nome = self.entry_novo_nome_mat.get().strip()
        
        if not selecionado or not novo_nome:
            return messagebox.showerror("Erro", "Selecione o material e preencha o novo nome!", parent=self)
        
        id_mat = int(selecionado.split(" - ")[0])
        material_antigo = self._cache_materiais.get(id_mat)
        
        if novo_nome.lower() != material_antigo.nome.lower():
            if novo_nome.lower() in [m.nome.lower() for m in self._cache_materiais.values()]:
                return messagebox.showwarning("Aviso", "Já existe outro material com esse nome!", parent=self)

        try:
            id_monitor = int(self.combo_monitor_resp.get().split(" - ")[0])
            self.servico_estoque.atualizar_material(id_mat, novo_nome, self.entry_novas_obs.get(), id_monitor=id_monitor)
            
            messagebox.showinfo("Sucesso", "Material atualizado!", parent=self)
            self.entry_novo_nome_mat.delete(0, 'end')
            self.entry_novas_obs.delete(0, 'end')
            self.atualizar_listas_mat()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar: {e}", parent=self)

    def btn_deletar_mat_click(self):
        selecionado = self.combo_deletar_mat.get()
        if not selecionado: return messagebox.showerror("Erro", "Selecione um material!", parent=self)
        
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar:\n{selecionado}?", parent=self):
            try:
                id_mat = int(selecionado.split(" - ")[0])
                id_monitor = int(self.combo_monitor_resp.get().split(" - ")[0])
                
                self.servico_estoque.deletar_material(id_mat, id_monitor=id_monitor)
                messagebox.showinfo("Sucesso", "Material deletado com sucesso!", parent=self)
                self.atualizar_listas_mat()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao deletar: {e}", parent=self)