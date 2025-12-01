import glob
import sys
import os

def obter_anos_disponiveis():
    """Varre a pasta ENEM para encontrar subdiretórios de anos (4 dígitos)"""
    if not os.path.exists('ENEM'):
        return []
    
    itens = os.listdir('ENEM')
    anos = []
    for item in itens:
        full_path = os.path.join('ENEM', item)
        # Verifica se é diretório e se o nome é um número de 4 dígitos (ex: 2019)
        if os.path.isdir(full_path) and item.isdigit() and len(item) == 4:
            anos.append(item)
    
    # Retorna ordenado do mais recente para o mais antigo
    return sorted(anos, reverse=True)

def gerar_menu_lateral(anos_encontrados, ano_atual):
    """Gera o HTML dos links para outros anos e o botão Voltar"""
    html = ""
    
    # --- BOTÃO VOLTAR ---
    # Aponta para o index principal que fica um nível acima (../index.html)
    html += '<a href="../index.html" style="background-color:#e0e0e0;">🏠 Voltar ao Início</a>'

    html += "<h3>Outros Anos</h3>"
    
    for ano in anos_encontrados:
        classe = 'class="active"' if ano == ano_atual else ''
        link = f"../{ano}/index.html"
        html += f'<a href="{link}" {classe}>{ano}</a>\n'
    return html

def criarArquivo(ano, menu_html):
    print(f"--> Processando índice para o ano: {ano}")
    
    template_path = "_08_enemANO.html"
    texto = ""
    
    if os.path.exists(template_path):
        with open(template_path, "r", encoding='utf-8') as f:
            texto = f.read()
    else:
        print(f"❌ Erro: Template {template_path} não encontrado.")
        return
    
    # 1. Substitui o Ano no Título
    texto = texto.replace('__ANO__', ano)
    
    # 2. Injeta o Menu Lateral (com botão voltar)
    texto = texto.replace('__MENU__', menu_html)

    # 3. Busca HTMLs interativos
    path_pattern = f'ENEM/{ano}/PROVAS_E_GABARITOS/*_INTERATIVO.html'
    arquivos = sorted(glob.glob(path_pattern))

    ss = '<div class="lista-provas">\n'
    
    if not arquivos:
        ss += '<p style="color: #666; padding: 20px; background:#fff; border:1px solid #eee;">Nenhuma prova processada encontrada nesta pasta.</p>'
    else:
        ss += '<ul>\n'
        for f in arquivos:
            nome_arquivo = os.path.basename(f)
            
            # Limpa o nome para exibição (Remove prefixos e sufixos técnicos)
            display_name = nome_arquivo.replace('_INTERATIVO.html', '')
            display_name = display_name.replace(f'ENEM_{ano}_', '') 
            display_name = display_name.replace('_', ' ')
            
            link_relativo = f'PROVAS_E_GABARITOS/{nome_arquivo}'
            
            ss += f'<li><a href="{link_relativo}" target="_blank">📄 {display_name}</a></li>\n'
        ss += '</ul>\n'
    
    ss += '</div>\n'

    # 4. Substitui a lista de arquivos e a quantidade
    texto = texto.replace('__ARQUIVOS__', ss)
    texto = texto.replace('__QTD__', str(len(arquivos)))

    # Salva o index.html dentro da pasta do ano
    output_dir = f'ENEM/{ano}'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'index.html')
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(texto)
        print(f"   ✅ Salvo: {output_path}")

# --- BLOCO PRINCIPAL ---
if __name__ == "__main__":
    # 1. Descobre quais anos existem na pasta ENEM
    anos_existentes = obter_anos_disponiveis()
    
    if not anos_existentes:
        print("❌ Nenhuma pasta de ano (ex: 2019, 2024) encontrada dentro de 'ENEM/'.")
        sys.exit(1)

    print(f"=================================================")
    print(f"Geração de Índices Individuais (Com botão Voltar)")
    print(f"Anos encontrados: {', '.join(anos_existentes)}")
    print(f"=================================================")

    # 2. Para cada ano existente, gera o índice com o menu atualizado
    for ano_atual in anos_existentes:
        menu = gerar_menu_lateral(anos_existentes, ano_atual)
        criarArquivo(ano_atual, menu)
        
    print(f"\n✅ Concluído!")