from concurrent.futures import ThreadPoolExecutor
import customtkinter as ctk
import tkinter as tk
from typing import Callable, Any, Optional

_pool = ThreadPoolExecutor(max_workers=4)

def rodar_em_background(
    janela: ctk.CTkBaseClass, 
    tarefa: Callable[..., Any], 
    callback_sucesso: Callable[[Any], None], 
    callback_erro: Optional[Callable[[Exception], None]] = None,
    *args, 
    **kwargs
) -> None:
    """
    Executa uma tarefa pesada em uma thread separada e retorna o resultado para a GUI.
    
    :param janela: Instância da janela principal (app) para agendar atualizações.
    :param tarefa: Função pesada a ser executada em background.
    :param callback_sucesso: Função executada na thread principal recebendo o resultado.
    *args e **kwargs: Argumentos passados automaticamente para a 'tarefa'.
    """
    def wrapper():
        try:
            resultado = tarefa(*args, **kwargs)
            
            if janela.winfo_exists():
                try:
                    janela.after(0, lambda: callback_sucesso(resultado))
                except tk.TclError:
                    pass 
                    
        except Exception as e:
            if janela.winfo_exists():
                try:
                    if callback_erro:
                        janela.after(0, lambda: callback_erro(e))
                    else:
                        print(f"Erro em background não tratado: {e}")
                except tk.TclError:
                    pass

    _pool.submit(wrapper)