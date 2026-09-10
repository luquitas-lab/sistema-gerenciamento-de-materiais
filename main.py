import customtkinter as ctk

from repositorios.conexao import GerenciadorConexao
from servicos.estoque_service import EstoqueService
from servicos.relatorios_service import RelatorioService
from servicos.checklist_service import ChecklistService

from telas.janela_monitor import JanelaMonitor
from telas.janela_material import JanelaMaterial
from telas.janela_movimentacoes import JanelaMovimentacoes
from telas.janela_checklist import JanelaChecklist
from telas.janela_historico_relatorio import JanelaHistorico, JanelaRelatorio

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gerenciamento de Materiais")
        self.configure(fg_color="#121212") 
        
        # Inicialização única de dependências
        self.gerenciador_conexao = GerenciadorConexao()
        self.estoque_service = EstoqueService(self.gerenciador_conexao)
        self.relatorios_service = RelatorioService(self.gerenciador_conexao)
        self.checklist_service = ChecklistService(self.gerenciador_conexao)
        
        self._configurar_geometria()
        self.protocol("WM_DELETE_WINDOW", self.fechar_sistema)
        self._construir_menu()

    def _configurar_geometria(self):
        largura_janela, altura_janela = 500, 680
        # Otimização de cálculo de tela
        pos_x = (self.winfo_screenwidth() - largura_janela) // 2
        pos_y = (self.winfo_screenheight() - altura_janela) // 2
        self.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

    def _construir_menu(self):
        self.frame_principal = ctk.CTkFrame(self, corner_radius=20, fg_color="#1e1e1e")
        self.frame_principal.pack(pady=40, padx=40, fill="both", expand=True)

        self.label_titulo = ctk.CTkLabel(self.frame_principal, text="📦 Menu Principal", 
                                        font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), 
                                        text_color="#e0e0e0")
        self.label_titulo.pack(pady=(30, 5))
        
        self.label_sub = ctk.CTkLabel(self.frame_principal, text="Gerenciamento de Estoque", 
                                    font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#888888")
        self.label_sub.pack(pady=(0, 25))

        btn_kwargs = {
            "width": 300,
            "height": 45,
            "corner_radius": 8,
            "font": ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            "anchor": "center", 
            "border_width": 1,         
            "border_color": "#444444",
            "fg_color": "#2a2a2a",      
            "text_color": "#ffffff",    
            "hover_color": "#3a3a3a"
        }

        pacote_servicos = {"estoque": self.estoque_service, "checklist": self.checklist_service}
        pacote_servicos_relatorio = {"estoque": self.estoque_service, "relatorios": self.relatorios_service}

        botoes = [
            ("  Gerenciar Monitores", JanelaMonitor, self.estoque_service),
            ("  Gerenciar Materiais", JanelaMaterial, self.estoque_service),
            ("  Registrar Entradas e Perdas", JanelaMovimentacoes, self.estoque_service),
            ("  Realizar Check-list Diário", JanelaChecklist, pacote_servicos),
            ("  Gerar Relatório de Estoque", JanelaRelatorio, pacote_servicos_relatorio),
            ("  Ver Histórico de Ações", JanelaHistorico, self.relatorios_service)
        ]

        for texto, classe, dependencia in botoes:
            btn = ctk.CTkButton(
                self.frame_principal, 
                text=texto, 
                command=lambda c=classe, dep=dependencia: self.abrir_tela(c, dep),
                **btn_kwargs
            )
            btn.pack(pady=8)

        btn_sair = ctk.CTkButton(
            self.frame_principal, text="Sair do Sistema", 
            command=self.fechar_sistema, 
            fg_color="#c0392b", hover_color="#a53125", text_color="#ffffff", 
            width=300, height=45, corner_radius=8, 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        btn_sair.pack(pady=(30, 20))

    def abrir_tela(self, ClasseDaJanela, dependencia):
        ClasseDaJanela(self, dependencia)

    def fechar_sistema(self):
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()