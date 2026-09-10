import sys
from pathlib import Path

# 1. DEFINIÇÃO DO DIRETÓRIO BASE
if getattr(sys, 'frozen', False):
    # Otimização: Garante que o caminho funcione perfeitamente se você compilar usando PyInstaller
    BASE_DIR = Path.home() / "Documents" / "Sistema_Materiais"
else:
    BASE_DIR = Path(__file__).resolve().parent

BASE_DIR.mkdir(parents=True, exist_ok=True)

# 2. CAMINHO DO BANCO DE DADOS
DB_PATH = BASE_DIR / 'materiais.db'

# 3. IDENTIFICADOR DA ÁREA DE TRABALHO
def _get_desktop_path() -> Path:
    home = Path.home()
    # Verifica em ordem as pastas mais prováveis
    possiveis_caminhos = [
        home / "OneDrive" / "Área de Trabalho",
        home / "OneDrive" / "Desktop",
        home / "Desktop",
        home / "Área de Trabalho"
    ]
    for caminho in possiveis_caminhos:
        if caminho.exists():
            return caminho
    return home / "Desktop" 

DESKTOP_PATH = _get_desktop_path()

# 4. DIRETÓRIOS DE EXPORTAÇÃO
PASTA_RELATORIOS = DESKTOP_PATH / "Relatorios_TXT"
PASTA_GRAFICOS = DESKTOP_PATH / "Graficos_Checklist"