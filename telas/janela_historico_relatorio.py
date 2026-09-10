import customtkinter as ctk
from tkinter import ttk, messagebox

class JanelaHistorico(ctk.CTkToplevel):
    def __init__(self, master, servico_relatorios):
        super().__init__(master)
        self.servico_relatorios = servico_relatorios
        self.title("Histórico de Movimentações")
        self.geometry("750x450")
        self.grab_set()

        colunas = ("ID", "Monitor", "Data", "Ação", "Detalhes")
        
        ctk.CTkLabel(self, text="🕒 Histórico de Movimentações", font=("Segoe UI", 20, "bold"), text_color="#e0e0e0").pack(pady=(15, 10))
        
        frame_tabela = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=10)
        frame_tabela.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#2a2a2a", foreground="#ffffff", relief="flat", borderwidth=0)
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=35, background="#1e1e1e", fieldbackground="#1e1e1e", foreground="#e0e0e0", borderwidth=0)
        style.map("Treeview", background=[('selected', '#3498db')])

        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        scrollbar = ctk.CTkScrollbar(frame_tabela, command=self.tree.yview)
        scrollbar.pack(side="right", fill="y", pady=5, padx=5)
        
        self.tree.configure(yscrollcommand=scrollbar.set)
        tamanhos_colunas = {"ID": 50, "Monitor": 120, "Data": 150, "Ação": 130, "Detalhes": 250}
        
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=tamanhos_colunas[col], anchor="w")
            
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        
        self.tree.tag_configure('par', background='#222222')
        self.tree.tag_configure('impar', background='#1e1e1e')
        self.carregar_historico()

    def carregar_historico(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            historico = self.servico_relatorios.listar_historico()
            for i, log in enumerate(historico):
                self.tree.insert("", "end", values=log, tags=('par' if i % 2 == 0 else 'impar',))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar histórico: {e}", parent=self)

class JanelaRelatorio(ctk.CTkToplevel):
    def __init__(self, master, servicos):
        super().__init__(master)
        
        self.servico_estoque = servicos["estoque"]
        self.servico_relatorios = servicos["relatorios"]
        
        self.title("Gerar Relatório")
        self.geometry("380x250")
        self.transient(master)
        self.grab_set()

        try:
            monitores = self.servico_estoque.listar_monitores_ativos()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar monitores: {e}", parent=self)
            self.destroy()
            return
        
        if not monitores:
            messagebox.showwarning("Aviso", "Cadastre um monitor primeiro!", parent=self)
            self.destroy()
            return

        self.lista_monitores = [f"{m.id_monitor} - {m.nome}" for m in monitores]

        ctk.CTkLabel(self, text="📄 Quem está gerando o relatório?", font=("Segoe UI", 15, "bold"), text_color="#e0e0e0").pack(pady=(25, 15))
        
        self.combo_monitores = ctk.CTkComboBox(self, values=self.lista_monitores, state="readonly", width=250, height=35)
        self.combo_monitores.set(self.lista_monitores[0])
        self.combo_monitores.pack(pady=10)
        
        ctk.CTkButton(self, text="Gerar Relatório", command=self.confirmar_e_gerar, 
                      fg_color="#2980b9", hover_color="#3498db", text_color="white",
                      font=("Segoe UI", 12, "bold"), height=40).pack(pady=20)

    def confirmar_e_gerar(self):
        nome_responsavel = self.combo_monitores.get().split(" - ", 1)[1]
        try:
            materiais_objetos = self.servico_estoque.listar_materiais_ativos()
            
            materiais_dicts = [
                {"id_material": m.id_material, "nome": m.nome, "quantidade": m.quantidade, "observacoes": m.observacoes} 
                for m in materiais_objetos
            ]
            
            caminho_arquivo = self.servico_relatorios.gerar_relatorio_inventario(nome_responsavel, materiais_dicts)
            messagebox.showinfo("Sucesso", f"Relatório gerado em:\n{caminho_arquivo}", parent=self)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar o relatório:\n{e}", parent=self)