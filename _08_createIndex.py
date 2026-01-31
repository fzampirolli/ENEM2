import os
import glob
import sys
from _09_createMainIndex import get_common_css, get_anos_links, BASE_DIR

def criar_index_ano(ano, anos_disponiveis):
    print(f"--> Processando índice do ano: {ano}")
    
    # Busca arquivos interativos
    path_pattern = f'ENEM/{ano}/PROVAS_E_GABARITOS/*_INTERATIVO.html'
    arquivos = sorted(glob.glob(path_pattern))

    lista_html = '<ul style="list-style: none; padding: 0;">'
    for f in arquivos:
        nome = os.path.basename(f)
        label = nome.replace('_INTERATIVO.html', '').replace('_', ' ')
        lista_html += f'<li style="margin-bottom:10px;"><a href="./PROVAS_E_GABARITOS/{nome}" class="btn-access" style="display:block; text-align:left; text-decoration:none;">📄 {label}</a></li>'
    lista_html += '</ul>'

    # Menu lateral com prefixo '../' porque estamos um nível abaixo
    menu_html = get_anos_links(anos_disponiveis, prefix="../")
    menu_html = f'<a href="../index.html" style="background-color:#eee;">🏠 Início</a>' + menu_html

    html = f"""<!doctype html><html lang="pt-br"><head><meta charset="utf-8"><title>ENEM {ano} - ENEM2</title>{get_common_css()}</head>
    <body><div id="header"><h1>ENEM Interativo {ano}</h1></div>
    <div class="main-container"><div id="nav">{menu_html}</div><div id="section">
    <h2>Cadernos Disponíveis</h2><p>Selecione uma prova para iniciar o simulado:</p>{lista_html}</div></div>
    <div id="footer">
    <p>Licença AGPLv3 | Projeto ENEM2 - {ano} | Desenvolvido na <a href=\"http://www.ufabc.edu.br\">UFABC</a></p>
    </div></body></html>"""

    output_path = f"ENEM/{ano}/index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"   ✅ Sucesso: {output_path}")

def criar_index_ano1(ano, anos):
    menu_html = get_anos_links(anos, prefix="../")
    provas = sorted(glob.glob(f"ENEM/{ano}/PROVAS_E_GABARITOS/*_INTERATIVO.html"))
    
    lista = ""
    for p in provas:
        nome = os.path.basename(p)
        lista += f'<a href="./PROVAS_E_GABARITOS/{nome}" class="btn-access" style="display:block; text-align:left; margin-bottom:10px;">📄 {nome.replace("_INTERATIVO.html", "")}</a>'

    html = f"""<html><head>{get_common_css()}</head><body>
    <div id="header"><h1>ENEM {ano}</h1></div>
    <div class="main-container"><div id="nav"><a href="../index.html">🏠 Início</a>{menu_html}</div>
    <div id="section"><h2>Cadernos Disponíveis</h2>{lista}</div></div></body></html>"""
    
    with open(f"ENEM/{ano}/index.html", "w") as f: f.write(html)

if __name__ == "__main__":
    anos = sorted([d for d in os.listdir(BASE_DIR) if d.isdigit()], reverse=True)
    for ano in anos:
        criar_index_ano(ano, anos)