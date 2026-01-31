import os
import glob

BASE_DIR = "ENEM"

def get_common_css():
    """Retorna o CSS unificado para todas as páginas do portal ENEM2."""
    return """
    <style>
        :root {
            --primary: #556B2F; /* DarkSeaGreen Escuro */
            --secondary: #8FBC8F; /* DarkSeaGreen Claro */
            --ufabc-blue: #074a8d;
            --light-bg: #f8f9fa;
            --sidebar-bg: #fdfdfd;
            --text-color: #333;
            --white: #ffffff;
            --shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            margin: 0; padding: 0; display: flex; flex-direction: column;
            min-height: 100vh; background-color: var(--light-bg);
            color: var(--text-color); line-height: 1.6;
        }
        #header {
            background-color: var(--primary); color: var(--white);
            text-align: center; padding: 40px 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        #header h1 { margin: 0; font-size: 2.2rem; font-weight: 300; letter-spacing: 1px; }
        .main-container {
            display: flex; flex: 1; max-width: 1200px; width: 100%;
            margin: -30px auto 40px; background: var(--white);
            border-radius: 12px; box-shadow: var(--shadow); overflow: hidden;
        }
        #nav { width: 260px; background-color: var(--sidebar-bg); padding: 40px 20px; border-right: 1px solid #eee; }
        #nav h3 { 
            color: var(--primary); font-size: 0.85rem; text-transform: uppercase; 
            margin: 25px 0 15px; border-bottom: 2px solid var(--secondary); padding-bottom: 5px;
        }
        #nav a {
            display: block; text-decoration: none; color: #555; padding: 12px 15px; 
            margin-bottom: 5px; border-radius: 8px; transition: 0.3s;
            font-weight: 500; border: 1px solid #eee; background: #fff;
        }
        #nav a:hover { background: var(--secondary); color: white; transform: translateX(5px); }
        #section { flex: 1; padding: 50px; }
        .hero-section { background: #f4f7f4; padding: 30px; border-radius: 10px; margin-bottom: 30px; border-left: 5px solid var(--primary); }
        .info-box { background: #eef6ff; padding: 25px; border-radius: 10px; border-left: 5px solid var(--ufabc-blue); margin: 30px 0; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; margin-top: 30px; }
        .year-card { background: var(--white); border: 1px solid #eee; border-radius: 15px; padding: 25px; text-align: center; transition: 0.3s; }
        .year-card:hover { transform: translateY(-10px); box-shadow: var(--shadow); border-color: var(--secondary); }
        .year-card h3 { font-size: 1.8rem; margin: 0; color: var(--primary); }
        .btn-access {
            display: inline-block; background: var(--primary); color: white !important;
            padding: 10px 20px; border-radius: 25px; margin-top: 15px; font-weight: 600;
        }
        #footer { background-color: #333; color: #bbb; text-align: center; padding: 30px; margin-top: auto; }
        #footer a { color: var(--secondary); text-decoration: none; }
        @media (max-width: 768px) { .main-container { flex-direction: column; margin-top: 0; border-radius: 0; } #nav { width: 100%; border-right: none; } }
    </style>
    """

def get_common_css1():
    return """
    <style>
        :root { --primary: #556B2F; --secondary: #8FBC8F; --ufabc-blue: #074a8d; --white: #fff; --light: #f8f9fa; }
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: var(--light); display: flex; flex-direction: column; min-height: 100vh; }
        #header { background: var(--primary); color: white; text-align: center; padding: 30px; }
        .main-container { display: flex; flex: 1; max-width: 1200px; width: 100%; margin: -20px auto 40px; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; }
        #nav { width: 250px; background: #fdfdfd; padding: 30px; border-right: 1px solid #eee; }
        #nav a { display: block; padding: 12px; margin-bottom: 8px; border: 1px solid #eee; border-radius: 8px; text-decoration: none; color: #444; font-weight: 500; transition: 0.3s; }
        #nav a:hover { background: var(--secondary); color: white; transform: translateX(5px); }
        #section { flex: 1; padding: 40px; }
        .info-box { background: #eef6ff; padding: 20px; border-left: 5px solid var(--ufabc-blue); border-radius: 8px; margin: 20px 0; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
        .year-card { border: 1px solid #eee; padding: 20px; border-radius: 15px; text-align: center; transition: 0.3s; }
        .year-card:hover { transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .btn-access { display: inline-block; background: var(--primary); color: white !important; padding: 10px 20px; border-radius: 20px; margin-top: 10px; text-decoration: none; font-weight: bold; }
        #footer { background: #333; color: #ccc; text-align: center; padding: 20px; }
    </style>
    """

def get_refs_html():
    """Bloco de referências unificado."""
    return """
 <div class="refs" style="margin-top: 40px; padding: 25px; background-color: #f9f9f9; border-radius: 8px; border: 1px solid #eee; font-size: 0.9em;">
        <h4 style="color: var(--ufabc-blue); margin-top: 0;">Referências Acadêmicas e Fontes</h4>
        <ul style="list-style-type: none; padding: 0; margin-bottom: 20px;">
            <li style="margin-bottom: 12px;">
                Zampirolli, F.A. et al. <strong>"<a href="https://ieeexplore.ieee.org/document/9725135" target="_blank">Interactive ENEM: exams with statistics and free access</a>"</strong>. LACLO2021.
            </li>
            <li>
                Zampirolli, F.A. et al. <strong>"<a href="https://ieeexplore.ieee.org/document/9725157" target="_blank">Experiments in selection processes of students for a crammer</a>"</strong>. LACLO2021.
            </li>
        </ul>
        <div style="padding-top: 15px; border-top: 1px solid #ddd; font-size: 0.85em;">
            <p><strong>Fontes:</strong> 
                <a href="https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem" target="_blank">INEP (Microdados)</a>, 
                <a href="https://github.com/pdf2htmlEX/pdf2htmlEX" target="_blank">pdf2htmlEX</a> e 
                <a href="https://cran.r-project.org/web/packages/ltm/" target="_blank">Pacote R ltm</a>.
            </p>
            <p style="margin: 10px 0;">
                <strong>Código Aberto:</strong> 
                🔗 <a href="https://github.com/fzampirolli/ENEM2" target="_blank">GitHub ENEM v2</a> | 
                🔗 <a href="https://github.com/fzampirolli/ENEM" target="_blank">GitHub ENEM v1</a>
            </p>
            <p><strong>Feedback:</strong> <a href="mailto:fzampirolli@ufabc.edu.br">fzampirolli@ufabc.edu.br</a></p>
        </div>
    </div>
    """


def get_anos_links(anos, prefix="./"):
    """Gera menu lateral. prefix='../' para páginas dentro de pastas."""
    menu_html = f'<a href="{prefix}statistics.html" style="background-color:#e8f5e9; border-color:#c8e6c9; color:#2e7d32;">📊 Metodologia TRI</a>'
    menu_html += "<h3>Anos Disponíveis</h3>"
    for ano in anos:
        menu_html += f'<a href="{prefix}{ano}/index.html">{ano}</a>'
    return menu_html

def criar_index(anos, menu_html):
    cards_html = '<div class="cards-grid">'
    for ano in anos:
        path_provas = os.path.join(BASE_DIR, ano, "PROVAS_E_GABARITOS", "*_INTERATIVO.html")
        qtd = len(glob.glob(path_provas))
        cards_html += f"""<div class="year-card"><h3>{ano}</h3><p><strong>{qtd}</strong> provas</p><a href="./{ano}/index.html" class="btn-access">Explorar</a></div>"""
    cards_html += '</div>'

    html = f"""<!doctype html><html lang="pt-br"><head><meta charset="utf-8"><title>ENEM Interativo - ENEM2</title>{get_common_css()}</head>
    <body><div id="header"><h1>ENEM Interativo <span style="font-size: 0.6em; opacity: 0.8;">v2.0</span></h1></div>
    <div class="main-container"><div id="nav">{menu_html}</div><div id="section">
    <div class="hero-section"><h2>Bem-vindo ao Projeto ENEM2</h2><p>Evolução do portal <a href="http://mctest.ufabc.edu.br:8000/ENEM" target="_blank">MCTest/ENEM</a>.</p></div>
    <h3>Selecione o ano:</h3>{cards_html}</div></div>
    <div id="footer">
    <p>Licença AGPLv3 | Projeto ENEM2 | Desenvolvido na <a href=\"http://www.ufabc.edu.br\">UFABC</a></p>
    </p></div>
    </body></html>"""
    
    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Principal: ENEM/index.html criado.")

def criar_index1(anos, menu_html):
    cards = ""
    for ano in anos:
        qtd = len(glob.glob(f"{BASE_DIR}/{ano}/PROVAS_E_GABARITOS/*_INTERATIVO.html"))
        cards += f'<div class="year-card"><h3>{ano}</h3><p>{qtd} provas</p><a href="./{ano}/index.html" class="btn-access">Acessar</a></div>'
    
    html = f"""<html><head>{get_common_css()}</head><body>
    <div id="header"><h1>ENEM Interativo v2.0</h1></div>
    <div class="main-container"><div id="nav">{menu_html}</div>
    <div id="section"><h2>Bem-vindo</h2><div class="info-box">Foco na TRI: Errar fáceis é pior que errar difíceis!</div>
    <div class="cards-grid">{cards}</div>{get_refs_html()}</div></div>
    <div id="footer">UFABC | 2026</div></body></html>"""
    with open(f"{BASE_DIR}/index.html", "w") as f: f.write(html)

def criar_statistics(anos, menu_html):
    """Cria a página statistics.html com TODO o conteúdo explicativo original."""
    html = f"""<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>Estatísticas e Metodologia - ENEM2</title>
  {get_common_css()}
</head>
<body>
<div id=\"header\">
  <h1>Metodologia e Estatísticas TRI</h1>
</div>

<div class=\"main-container\">
    <div id=\"nav\">
      <a href=\"./index.html\" style=\"background-color:#eee; margin-bottom:20px;\">🏠 Voltar ao Início</a>
      {menu_html}
    </div>

    <div id=\"section\">
      <h2>Entendendo as Estatísticas</h2>

      <div class=\"info-box\">
        <p><strong>Dica de Estudo:</strong> Errar as questões <em>fáceis</em> é muito pior do que errar as difíceis 
        <span style=\"color: var(--ufabc-blue)\">(devido à Teoria de Resposta ao Item utilizada pelo ENEM)</span>! 
        <a href=\"https://www.loom.com/share/658b8e7a2e214252a950326b73bbef92\" target=\"_blank\">▶️ Veja um vídeo explicativo aqui.</a></p>
      </div>

      <p>Ao clicar no botão de estatísticas no final de cada exame interativo, uma nova página se abre contendo o gabarito e gráficos detalhados.</p>

      <h3>1. Curva Característica do Item (CCI)</h3>
      <p>Estes gráficos mostram a CCI da Teoria de Resposta ao Item (TRI), calculada via modelo <strong>3PL</strong> (Três Parâmetros Logísticos):</p>
      
      

      <ul style=\"line-height: 1.8;\">
        <li><strong>Parâmetro a (Discriminação):</strong> Capacidade da questão de diferenciar alunos com maior e menor proficiência.</li>
        <li><strong>Parâmetro b (Dificuldade):</strong> Nível de habilidade necessário para ter 50% de chance de acerto.</li>
        <li><strong>Parâmetro c (Acerto Casual/Chute):</strong> Probabilidade de um aluno com baixa proficiência acertar a questão.</li>
      </ul>

      <p>Teste os parâmetros neste 
        <a href=\"https://colab.research.google.com/drive/1ka7_SR_QB4G7ZPVvH3p_E0bZEbOH1vhK\" target=\"_blank\"><strong>Google Colab Interativo</strong></a>.
      </p>

      <h3>2. Estatísticas Descritivas e Distribuição</h3>
      <p>Apresentamos também a <strong>Média</strong> e o <strong>Desvio Padrão</strong> da amostra processada.</p>

      <h3>3. BoxPlot e ViolinPlot</h3>
      <p>Visualização da distribuição das frequências de acertos e erros em relação à proficiência dos candidatos, permitindo identificar padrões de comportamento dos estudantes.</p>

      {get_refs_html()}
    </div>
</div>

<div id=\"footer\">
    <p>Licença AGPLv3 | Projeto ENEM2 | Desenvolvido na <a href=\"http://www.ufabc.edu.br\">UFABC</a></p>
</div>
</body></html>"""
    
    with open(os.path.join(BASE_DIR, "statistics.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Sucesso: ENEM/statistics.html criado com conteúdo completo.")

def criar_statistics1(anos, menu_html):
    html = f"""<html><head>{get_common_css()}</head><body>
    <div id="header"><h1>Estatísticas e Metodologia</h1></div>
    <div class="main-container"><div id="nav"><a href="./index.html">🏠 Início</a>{menu_html}</div>
    <div id="section">
        <h2>Metodologia TRI (Modelo 3PL)</h2>
        <div class="info-box">Estudamos <strong>Discriminação (a)</strong>, <strong>Dificuldade (b)</strong> e <strong>Chute (c)</strong>.</div>
        <p>Abaixo a Curva Característica do Item (CCI):</p>
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/IRT_3PL.png/400px-IRT_3PL.png" style="max-width:100%; border-radius:8px;">
        <p>Pratique no <a href="https://colab.research.google.com/drive/1ka7_SR_QB4G7ZPVvH3p_E0bZEbOH1vhK" target="_blank">Google Colab</a> ou veja o <a href="https://www.loom.com/share/658b8e7a2e214252a950326b73bbef92" target="_blank">Vídeo Explicativo</a>.</p>
        {get_refs_html()}
    </div></div></body></html>"""
    with open(f"{BASE_DIR}/statistics.html", "w") as f: f.write(html)

if __name__ == "__main__":
    if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
    anos = sorted([d for d in os.listdir(BASE_DIR) if d.isdigit()], reverse=True)
    menu = get_anos_links(anos)
    criar_index(anos, menu)
    criar_statistics(anos, menu)