import os
import glob

# Configurações de Diretório
BASE_DIR = "ENEM"

def get_common_css():
    """Retorna o CSS compartilhado para garantir consistência visual."""
    return """
    <style>
        :root {
            --primary: #556B2F; /* DarkSeaGreen Escuro */
            --secondary: #8FBC8F; /* DarkSeaGreen Claro */
            --light-bg: #f8f9fa;
            --sidebar-bg: #f0f0f0;
            --text-color: #333;
            --link-color: #074a8d;
            --white: #ffffff;
        }

        * { box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            background-color: var(--light-bg);
            color: var(--text-color);
            line-height: 1.6;
        }

        /* Header */
        #header {
            background-color: var(--primary);
            color: var(--white);
            text-align: center;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            z-index: 10;
        }
        #header h1 { margin: 0; font-weight: 400; letter-spacing: 1px; }

        /* Layout Flex para Corpo (Menu + Conteúdo) */
        .main-container {
            display: flex;
            flex: 1; /* Ocupa o espaço restante */
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
        }

        /* Menu Lateral (Nav) */
        #nav {
            width: 220px;
            background-color: var(--sidebar-bg);
            padding: 30px 20px;
            border-right: 1px solid #e0e0e0;
            flex-shrink: 0; /* Não encolhe */
        }
        
        #nav h3 { 
            margin-top: 0; 
            color: var(--primary); 
            font-size: 0.9rem; 
            text-transform: uppercase; 
            border-bottom: 2px solid var(--secondary);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }

        #nav a {
            display: block;
            text-decoration: none;
            color: #555;
            padding: 10px 15px;
            margin-bottom: 8px;
            border-radius: 6px;
            transition: all 0.2s ease;
            font-weight: 600;
            background: #fff;
            border: 1px solid #ddd;
        }

        #nav a:hover {
            background-color: var(--secondary);
            color: var(--white);
            transform: translateX(5px);
            border-color: var(--secondary);
        }

        /* Conteúdo Principal (Section) */
        #section {
            flex: 1;
            padding: 40px;
            background-color: var(--white);
        }

        h2 { color: var(--primary); border-bottom: 1px solid #eee; padding-bottom: 15px; margin-top: 0; }
        
        p { margin-bottom: 1.2rem; font-size: 1.05rem; }
        
        a { color: var(--link-color); text-decoration: none; font-weight: 500; }
        a:hover { text-decoration: underline; }

        /* Footer */
        #footer {
            background-color: var(--secondary);
            color: var(--white);
            text-align: center;
            padding: 20px;
            margin-top: auto;
        }
        #footer img { vertical-align: middle; margin: 0 10px; }
        #footer a { color: var(--white); }

        /* Estilos Específicos para Cards (Index) */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .year-card {
            background: white;
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        .year-card:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
        .year-card h3 { font-size: 2.5rem; margin: 10px 0; color: var(--primary); }
        .year-card p { font-size: 0.9rem; color: #777; }
        .btn-access {
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            margin-top: 15px;
            font-size: 0.9rem;
        }
        .btn-access:hover { background: #3e4f22; text-decoration: none; }

        /* Responsividade */
        @media (max-width: 768px) {
            .main-container { flex-direction: column; }
            #nav { width: 100%; border-right: none; border-bottom: 1px solid #ddd; }
            #nav a { display: inline-block; margin-right: 10px; }
        }
    </style>
    """

def get_anos_links(anos):
    """Gera o HTML do menu lateral."""
    menu_html = ""
    # Link estático para Estatísticas
    menu_html += f'<a href="./statistics.html" style="background-color:#e8f5e9; border-color:#c8e6c9; color:#2e7d32;">📊 Estatísticas</a>'
    
    menu_html += "<h3>Anos Disponíveis</h3>"
    
    if not anos:
        menu_html += "<p>Nenhum ano encontrado.</p>"
    
    for ano in anos:
        menu_html += f'<a href="./{ano}/index.html">{ano}</a>'
    
    return menu_html

def criar_index(anos, menu_html):
    """Cria o arquivo ENEM/index.html (Landing Page)"""
    
    # Prepara o grid de cards
    cards_html = '<div class="cards-grid">'
    for ano in anos:
        # Conta provas
        path_provas = os.path.join(BASE_DIR, ano, "PROVAS_E_GABARITOS", "*_INTERATIVO.html")
        qtd = len(glob.glob(path_provas))
        
        cards_html += f"""
        <div class="year-card">
            <h3>{ano}</h3>
            <p>{qtd} Provas Processadas</p>
            <a href="./{ano}/index.html" class="btn-access">Acessar Provas</a>
        </div>
        """
    cards_html += '</div>'

    html = f"""<!doctype html>
<html class="no-js" lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>ENEM Interativo - Início</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {get_common_css()}
</head>
<body>

<div id="header">
  <h1>ENEM Interativo</h1>
  <p>Portal de Microdados e Provas Interativas</p>
</div>

<div class="main-container">
    <div id="nav">
      {menu_html}
    </div>

    <div id="section">
      <h2>Bem-vindo ao ENEM Interativo</h2>
      <p>Este portal organiza as provas do ENEM, permitindo que estudantes resolvam as questões de forma interativa, cronometrada e com acesso a estatísticas detalhadas baseadas na Teoria de Resposta ao Item (TRI).</p>
      
      <p>Selecione um ano abaixo ou no menu lateral para começar:</p>
      
      {cards_html}

      <hr style="margin-top: 40px; border: 0; border-top: 1px solid #eee;">
      
      <p style="font-size: 0.9em; color: #666;">
        <strong>Nota:</strong> O sistema utiliza dados oficiais do INEP e algoritmos estatísticos (3PL) para gerar gráficos de desempenho e dificuldade das questões.
      </p>
    </div>
</div>

<div id="footer">
  <p>
    <a href="https://www.gnu.org/licenses/agpl-3.0.html" target="_blank">Licença AGPLv3</a> | 
    Desenvolvido na <a href="http://www.ufabc.edu.br" target="_blank" style="text-decoration:underline;">UFABC</a>
  </p>
</div>

</body>
</html>
    """
    
    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ ENEM/index.html criado com sucesso.")

def criar_statistics(anos, menu_html):
    """Cria o arquivo ENEM/statistics.html (Página Informativa)"""
    
    html = f"""<!doctype html>
<html class="no-js" lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>ENEM Interativo - Estatísticas</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {get_common_css()}
</head>
<body>

<div id="header">
  <h1>ENEM Interativo</h1>
  <p>Sobre as Estatísticas e Metodologia</p>
</div>

<div class="main-container">
    <div id="nav">
      <a href="./index.html" style="background-color:#e0e0e0;">🏠 Voltar ao Início</a>
      {menu_html}
    </div>

    <div id="section">

      <h2>Entendendo as Estatísticas</h2>

      <div style="background: #e8f5e9; padding: 20px; border-left: 5px solid var(--primary); margin-bottom: 25px; border-radius: 4px;">
        <p style="margin:0;"><strong>Dica de Estudo:</strong> Errar as questões *fáceis* é muito pior do que errar as difíceis 
        <span style="color: #074a8d">(devido à Teoria de Resposta ao Item utilizada pelo ENEM para atribuir as habilidades/pontuações)</span>! 
        <a href="https://www.loom.com/share/658b8e7a2e214252a950326b73bbef92" target="_blank">Veja um vídeo explicativo aqui.</a></p>
      </div>

      <p>Ao clicar no botão de estatísticas no final de cada exame interativo, uma nova página se abre contendo o gabarito, suas respostas e gráficos detalhados.</p>

      <h3>1. Curva Característica do Item (CCI)</h3>
      <p>Estes gráficos mostram a CCI da Teoria de Resposta ao Item (TRI), calculados através de uma amostra aleatória de estudantes (ex: 10.000). O modelo utilizado é o <strong>3PL</strong> (Três Parâmetros Logísticos).</p>
      
      <ul style="margin-bottom: 20px; line-height: 1.8;">
        <li><strong>Parâmetro a (Discriminação):</strong> Capacidade da questão de diferenciar alunos com maior e menor proficiência.</li>
        <li><strong>Parâmetro b (Dificuldade):</strong> Nível de habilidade necessário para ter 50% de chance de acerto (desconsiderando o chute).</li>
        <li><strong>Parâmetro c (Acerto Casual/Chute):</strong> Probabilidade de um aluno com baixa proficiência acertar a questão.</li>
      </ul>

      <p>Para testar diferentes valores de a, b e c, você pode utilizar este 
        <a href="https://colab.research.google.com/drive/1ka7_SR_QB4G7ZPVvH3p_E0bZEbOH1vhK" target="_blank" style="font-weight:bold;">Google Colab Interativo</a>.
      </p>

      <h3>2. Estatísticas Descritivas</h3>
      <p>Nos gráficos também são apresentados:</p>
      <ul>
        <li><strong>Média:</strong> Valor entre 0 (todos erraram) e 1 (todos acertaram) na amostra.</li>
        <li><strong>Desvio Padrão (std):</strong> Variação das respostas na amostra.</li>
      </ul>

      <h3>3. BoxPlot e ViolinPlot</h3>
      <p>Geramos também gráficos de BoxPlot combinados com ViolinPlot para melhor visualizar a distribuição das frequências de acertos (1) e erros (0) em relação à proficiência dos candidatos.</p>

      <hr>

      <p style="font-size: 0.9rem; color: #666;">
        <em>Nota: Esses gráficos estão disponíveis preferencialmente para exames onde foi possível extrair uma amostra significativa (superior a 1.000 ou 10.000 estudantes).</em>
      </p>

      <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd;">
          <p><span style="color: #074a8d; font-size: 14px"><strong>Fontes de Dados e Tecnologia:</strong> <a
            href="https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem" target="_blank">INEP (Microdados)</a>,
            <a href="https://github.com/pdf2htmlEX/pdf2htmlEX" target="_blank">pdf2htmlEX</a> e
              <a href="https://cran.r-project.org/web/packages/ltm" target="_blank">Pacote R ltm</a>.</span>
          </p>

          <p><strong>Ajude a melhorar este serviço gratuito:</strong><br>
            <a href="https://levantamento.ufabc.edu.br/index.php/293112" target="_blank">Preencha o Formulário de Feedback</a> ou
            <a href="mailto:fzampirolli@ufabc.edu.br" target="_blank">Envie um Email</a>.<br>
            <span style="color: dodgerblue; font-size: 13px">
              (Disponibilidade de anos anteriores depende do retorno positivo neste formulário)</span>
          </p>
          
          <p><span style="color: #074a8d; font-size: 14px"><strong>Referência / Publicação:</strong></span><br>
            Zampirolli, F.A.; Antunes Jr, I.; Steil, L.; Teodoro Jr, L.<br>
            "Interactive ENEM: exams with statistics and free access". <a href="https://www.laclolala.com/#/laclo" target="_blank">LACLO2021</a>
            - <a href="http://mctest.ufabc.edu.br:8000/static/__LACLO21_enem.pdf" target="_blank">SLIDES</a><br>
            <a href="working.html">Trabalhos futuros</a>
          </p>
      </div>

    </div>
</div>

<div id="footer">
  <a href="https://www.gnu.org/licenses/agpl-3.0.html"><img
    src="./img/agplv3.png" style="width:60px;height:30px;" alt="License"></a>
  <br>Copyright © 2021 - <a href="http://www.ufabc.edu.br" style="color:white">UFABC</a>
</div>

</body>
</html>
    """
    
    with open(os.path.join(BASE_DIR, "statistics.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ ENEM/statistics.html criado com sucesso.")

if __name__ == "__main__":
    if not os.path.exists(BASE_DIR):
        print(f"❌ Pasta {BASE_DIR} não encontrada. Execute na raiz do projeto.")
        exit(1)

    # 1. Detecta anos
    itens = os.listdir(BASE_DIR)
    anos = []
    for item in itens:
        path = os.path.join(BASE_DIR, item)
        if os.path.isdir(path) and item.isdigit() and len(item) == 4:
            anos.append(item)
    anos.sort(reverse=True)

    # 2. Gera Menu Comum
    menu = get_anos_links(anos)

    # 3. Gera Páginas
    criar_index(anos, menu)
    criar_statistics(anos, menu)