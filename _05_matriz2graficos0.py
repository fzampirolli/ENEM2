'''
=====================================================================
Copyright (C) 2021 UFABC, developed by Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of "ENEM Interativo".
=====================================================================
'''

import json
import glob
import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from PIL import Image
from tqdm import tqdm

# --- CONFIGURAÇÃO INICIAL ---
warnings.filterwarnings("ignore")

# Configurações de Resolução de Imagem (Alta Qualidade)
DPI_resolution = 200
# Ajustei a resolução base para manter a proporção correta na exportação
width_resolution = 2000 
height_resolution = 1600

# --- PALETA DE CORES (PASTEL & PROFESSIONAL) ---
COLOR_BG       = "#FDFCF6"  # Creme suave
COLOR_AXIS     = "#FFFFFF"  # Branco
COLOR_GRID     = "#E5E7E9"  # Cinza claro
COLOR_TEXT     = "#4a5568"  # Cinza escuro profissional

# Cores do Gráfico Violin
COLOR_VIOLIN_FILL = "rgba(168, 218, 181, 0.6)" # Verde Pastel Suave
COLOR_VIOLIN_LINE = "#88B04B"                  # Verde Olíva (Contorno)
COLOR_BOX_LINE    = "#5DADE2"                  # Azul Pastel Forte
COLOR_MEAN        = "#EC7063"                  # Vermelho Pastel Suave
COLOR_Q_TEXT      = "#2E86C1"                  # Azul Escuro (Texto Q1/Q3)

def carregar_ranking(ano):
    """Carrega o ranking para obter Área e Cor das questões."""
    path = os.path.join("ENEM", ano, "DADOS", f"ranking_provas_{ano}.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return {str(item['co_prova']): item for item in json.load(f)}
    return {}

def plot_TRI(a, b, c, D, media, mediana, std, f, TAM, i, titulo_custom=""):
    """
    Gera o gráfico da Curva Característica do Item (CCI).
    """
    theta_max = 5
    theta = np.arange(-theta_max, theta_max, .05)
    
    c = max(0, min(1, c))
    irt = c + (1 - c) / (1 + np.exp(-D * a * (theta - b)))
    
    plt.clf()
    fig = plt.figure(figsize=(10, 7), facecolor=COLOR_BG)
    ax = plt.gca()
    ax.set_facecolor(COLOR_AXIS)

    # ... (Títulos e labels mantidos iguais) ...
    #plt.title(f"Curva Característica do Item (CCI) - Questão {i}", fontsize=18, fontweight='bold', color=COLOR_TEXT, pad=20)
    plt.title(f"Curva Característica do Item (CCI) {titulo_custom}", fontsize=18, fontweight='bold', color=COLOR_TEXT, pad=20)
    
    if -1 < b <= 1:
        xlabel_text = "Habilidade ($\theta$): b próximo de 0 (Item Médio)"
    elif 1 < b <= 3:
        xlabel_text = "Habilidade ($\theta$): Item Difícil"
    elif b > 3:
        xlabel_text = "Habilidade ($\theta$): Item Muito Difícil"
    elif -3 < b <= -1:
        xlabel_text = "Habilidade ($\theta$): Item Fácil"
    elif b <= -3:
        xlabel_text = "Habilidade ($\theta$): Item Muito Fácil"
    else:
        xlabel_text = "Habilidade ($\theta$)"
    
    plt.xlabel(xlabel_text, fontsize=14, color=COLOR_TEXT)

    # Calcula o ponto y exato em b pela fórmula (mais preciso que pegar do array)
    # P(b) = c + (1-c)/2 = (1+c)/2
    y_at_b = (1 + c) / 2

    plt.grid(True, linestyle='--', alpha=0.5, color=COLOR_GRID, zorder=0)

    # Elementos do Gráfico
    plt.hlines(c, -4, 4, colors="#F7DC6F", linestyles='--', linewidth=2, zorder=2)
    plt.scatter(-4, c, color="#F7DC6F", s=100, zorder=10, clip_on=False, edgecolors=COLOR_TEXT)
    plt.text(-3.8, c + 0.02, f'c={c:.2f}', color=COLOR_TEXT, fontsize=12, fontweight='bold', ha='left', va='bottom')

    plt.vlines(b, 0, y_at_b, linestyle='--', color="#85C1E9", linewidth=2, zorder=2)
    ax.annotate(f'b = {b:.2f}\n(Dificuldade)', xy=(b, 0.02), xytext=(b + 0.8, 0.15),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-.2", color=COLOR_TEXT),
                fontsize=12, color=COLOR_TEXT, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#85C1E9", alpha=0.9))

    # --- CORREÇÃO DA TANGENTE ---
    x_range = np.arange(b - 1.2, b + 1.2, .1)
    
    # Fórmula correta da derivada no ponto de inflexão para 3PL
    # Slope = D * a * (1 - c) / 4
    slope = (D * a * (1 - c)) / 4.0
    
    def tangent_line_func(x_val):
        return slope * (x_val - b) + y_at_b

    plt.plot(x_range, tangent_line_func(x_range), color="#F1948A", linestyle='-', linewidth=3, alpha=0.8, zorder=4)
    # ----------------------------
    
    offset_text_a = -1.5 if b > 0 else 1.5
    # Ajustei levemente a posição do texto para não sobrepor a reta corrigida
    ax.annotate(f'a = {a:.2f}\n(Discriminação)', xy=(b - 0.1, y_at_b), xytext=(b + offset_text_a, y_at_b + 0.20),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color=COLOR_TEXT),
                fontsize=12, color=COLOR_TEXT, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#F1948A", alpha=0.9))

    plt.plot(theta, irt, color="#7DCEA0", linewidth=4, zorder=3)
    plt.fill_between(theta, irt, alpha=0.15, color="#7DCEA0", zorder=1)
    plt.scatter(b, y_at_b, color="#E74C3C", s=120, zorder=5, edgecolors='white', linewidth=2)

    # Legenda Superior Direita (Mantida)
    stats_text = (
        r"$\bf{Estatísticas}$" + "\n"
        f"Amostras: {TAM}\n"
        f"Média: {media:.3f}\n"
        f"Mediana: {mediana:.3f}\n"
        f"D.P.: {std:.3f}\n"
        f"------------------\n"
        r"$\bf{Parâmetros\ TRI}$" + "\n"
        f"a: {a:.3f}\n"
        f"b: {b:.3f}\n"
        f"c: {c:.3f}"
    )
    props = dict(boxstyle='round,pad=0.6', facecolor='white', alpha=0.85, edgecolor='#DDDDDD')
    plt.text(0.97, 0.97, stats_text, transform=ax.transAxes, fontsize=11, verticalalignment='top', horizontalalignment='right', bbox=props, color='#333333')

    plt.ylim(-0.02, 1.05)
    plt.xlim(-4, 4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_TEXT)
    ax.spines['bottom'].set_color(COLOR_TEXT)
    ax.tick_params(colors=COLOR_TEXT, labelsize=12)
    plt.tight_layout()
    plt.savefig(f, dpi=DPI_resolution, bbox_inches='tight', facecolor=COLOR_BG)
    plt.close('all')
    
def drawViolinPlot(f, vet, i, titulo_custom=""):
    """
    Gera um gráfico de Violino proporcional, centralizado e com fontes grandes
    adequadas para exportação em alta resolução.
    """

    vet = vet[~np.isnan(vet)]
    
    if len(vet) == 0:
        print(f"⚠️ Aviso: Dados insuficientes para gerar Violin Plot da questão {i}. Pulando.")
        return
    
    s = f'Questão {i}'

    # Estatísticas
    q1 = np.percentile(vet, 25)
    q3 = np.percentile(vet, 75)
    media = np.mean(vet)
    n_amostras = len(vet)

    # --- Configuração de Tamanhos (SCALING) ---
    # Como a imagem final é grande (2000px+), precisamos de fontes grandes
    FONT_TITLE = 40
    FONT_AXIS = 32
    FONT_ANNOT = 28
    FONT_LEGEND = 26
    LINE_WIDTH = 4

    fig = go.Figure()

    # --- Violino ---
    # Configuração 'spanmode' manual ou width manual não são necessários se o layout for bom.
    fig.add_trace(go.Violin(
        y=vet,
        box_visible=True,
        meanline_visible=True,
        line_color=COLOR_VIOLIN_LINE,
        line_width=3,                 # Linha externa mais grossa
        fillcolor=COLOR_VIOLIN_FILL,
        opacity=0.8,
        x0=s,
        points=False,
        showlegend=False,
        # Boxplot Interno (Transparente com borda grossa)
        box=dict(
            fillcolor="rgba(0,0,0,0)", 
            line=dict(color=COLOR_BOX_LINE, width=LINE_WIDTH)
        ),
        # Linha da Média
        meanline=dict(color=COLOR_MEAN, width=LINE_WIDTH)
    ))

    # --- Anotações Internas (Q1, Média, Q3) ---
    anotacoes = [
        (q1, 'Q1', -0.35, COLOR_Q_TEXT), # x_shift negativo = esquerda
        (media, 'Média', 0.35, COLOR_MEAN), # x_shift positivo = direita
        (q3, 'Q3', -0.35, COLOR_Q_TEXT)
    ]

    for valor, txt, x_shift, cor in anotacoes:
        # Usamos x_shift (coordenada relativa) para afastar do centro do violino
        fig.add_annotation(
            x=s, y=valor,
            text=f"<b>{txt}</b>",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=3,
            ax=x_shift * 200, # Aumenta a distância da seta
            ay=0,
            arrowcolor=cor,
            font=dict(size=FONT_ANNOT, color=cor),
            bgcolor="rgba(255,255,255,0.7)", # Fundo semi-transparente para leitura
            borderpad=4
        )

    # --- Legenda Lateral (Annotation Box) ---
    # Cria uma caixa bonita no canto superior direito com fundo semi-transparente
    legenda_html = (
        f"<span style='font-size:{FONT_TITLE}px; font-weight:bold; color:{COLOR_TEXT}'>Estatísticas</span><br>"
        f"<span style='color:{COLOR_Q_TEXT}; font-weight:bold'>Q3: {q3:.2f}</span><br>"
        f"<span style='color:{COLOR_MEAN}; font-weight:bold'>Média: {media:.2f}</span><br>"
        f"<span style='color:{COLOR_Q_TEXT}; font-weight:bold'>Q1: {q1:.2f}</span><br><br>"
        f"<span style='color:{COLOR_TEXT}'>Amostras: {n_amostras}</span>"
    )

    fig.add_annotation(
        text=legenda_html,
        align="left",
        showarrow=False,
        xref="paper", yref="paper",
        x=0.98, y=0.98,          # Canto superior direito
        xanchor="right", yanchor="top",
        bgcolor="rgba(255,255,255,0.85)", # Fundo levemente transparente
        bordercolor=COLOR_GRID,
        borderwidth=2,
        font=dict(size=FONT_LEGEND)
    )

    # --- Layout Otimizado ---
    fig.update_layout(
        # Tamanho do Layout interno (Base para cálculo de fontes)
        width=1400, 
        height=1200, 
        
        title_text=f"Distribuição de Acertos {titulo_custom}",
        title_font_size=FONT_TITLE,
        title_x=0.5, # Centraliza o título
        
        # Margens equilibradas para centralizar o violino
        margin=dict(l=150, r=150, t=100, b=100),
        
        plot_bgcolor=COLOR_BG,
        paper_bgcolor=COLOR_BG,
        
        # Eixos
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            tickfont=dict(size=FONT_TITLE, color=COLOR_TEXT, family="Arial Black")
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor=COLOR_GRID, 
            zeroline=False,
            tickfont=dict(size=FONT_AXIS, color=COLOR_TEXT)
        )
    )

    try:
        # Exportação usando Kaleido
        # width/height aqui definem a resolução final do pixel
        fig.write_image(f, width=width_resolution, height=height_resolution)
        # print(f"   Salvo: {os.path.basename(f)}") # Debug opcional
    except ValueError as e:
        print(f"⚠️ Erro de Valor ao salvar Violin Plot {i}: {e}")
    except Exception as e:
        print(f"⚠️ Erro ao salvar Violin Plot {i}: {e}")
        print("   DICA: Verifique se o pacote 'kaleido' está instalado: pip install -U kaleido")

def draw_signoits(output_folder, filename_base, mat, mat_raw, ranking):
    nome_arquivo = os.path.basename(filename_base)
    # Ex: 505_000100_data_TRI.csv
    partes = nome_arquivo.split('_')
    
    # O ID da prova é SEMPRE a primeira parte
    codigo_original = partes[0] 
    
    # A amostra é SEMPRE a segunda parte
    tam = partes[1].zfill(6) 

    # Se o ID original contiver um par (ex: 508_512), o split resolve
    codigos = codigo_original.split('_')

    print(f"   -> Processando: {codigo_original} | Amostra: {tam}")
    
    for codigo in codigos:
        # Busca metadados no ranking para o título
        meta = ranking.get(str(codigo), {})
        area = meta.get('sg_area', 'NI')
        cor = meta.get('tx_cor', 'NI')
        print(f"      → Processando código {codigo} ({area} - {cor})...")
        
        for i in tqdm(range(mat.shape[0]), desc=f"Prova {codigo}", unit="img"):
            a, b, c, m, st, med = mat[i][0], mat[i][1], mat[i][2], mat[i][3], mat[i][4], mat[i][5]
            D = 1.7

            questao_titulo = f"Questão {i+1} - {area} ({cor})"

            q_id = str(i + 1) # Simplificado para exemplo

            # TRI
            #fimg_tri = os.path.join(output_folder, f"{codigo}_{str(i + 1).zfill(3)}_fig_tri_{tam}.png")
            fimg_tri = os.path.join(output_folder, f"{codigo}_{q_id}_fig_tri_{tam}.png")
            if not os.path.exists(fimg_tri):
                plot_TRI(a, b, c, D, m, med, st, fimg_tri, tam, i + 1, titulo_custom=questao_titulo) # Passando o número da questão

            # Violin
            if i < mat_raw.shape[1]:
                dados_item = mat_raw[:, i]
                #fimg_box = os.path.join(output_folder, f"{codigo}_{str(i + 1).zfill(3)}_fig_box_{tam}.png")
                fimg_box = os.path.join(output_folder, f"{codigo}_{q_id}_fig_box_{tam}.png")
                if not os.path.exists(fimg_box):
                    drawViolinPlot(fimg_box, dados_item, i + 1, titulo_custom=questao_titulo)

def genStatistics(ano):
    # --- CAMINHOS ATUALIZADOS ---
    input_dir = f"./ENEM/{ano}/DADOS/MATRIZ"
    output_dir = f"./ENEM/{ano}/FIGS"
    # ----------------------------

    print(f"="*60)
    print(f"Gerando Gráficos para o ano {ano}")
    print(f"Entrada: {input_dir}")
    print(f"Saída:   {output_dir}")
    print(f"="*60)

    if not os.path.exists(input_dir):
        print(f"❌ Erro: Diretório {input_dir} não encontrado.")
        return
    
    os.makedirs(output_dir, exist_ok=True)

    files_tri = sorted(glob.glob(os.path.join(input_dir, '*_TRI.csv')))
    
    if not files_tri:
        print("⚠️  Nenhum arquivo _TRI.csv encontrado.")
        return
    
    # Dentro de genStatistics...
    ranking = carregar_ranking(ano)

    for f_tri in files_tri:
        print(f"\nProcessando: {os.path.basename(f_tri)}")
        f_data = f_tri.replace('_TRI.csv', '.csv')
      
        if not os.path.exists(f_data):
            print(f"❌ Erro: Dados brutos não encontrados: {f_data}")
            continue

        try:
            df_mat = pd.read_csv(f_data, sep=',', header=None)
            df_tri = pd.read_csv(f_tri, sep=',')
        except Exception as e:
            print(f"Erro CSV: {e}")
            continue

        mat_respostas = df_mat.to_numpy()
        
        # Atualiza o tamanho da amostra com o valor real da matriz
        n_amostras_real = mat_respostas.shape[0]
        
        # Verifica se deve pular com base no número real de linhas
        if n_amostras_real < 100:
            print(f"⚠️  Matriz com {n_amostras_real} linhas (< 100). Pulando geração de gráficos.")
            continue

        v_mean = np.mean(mat_respostas, axis=0)
        v_std = np.std(mat_respostas, axis=0)
        v_median = np.median(mat_respostas, axis=0)

        if 'Discrimination' in df_tri.columns:
            mat_tri_params = df_tri[['Discrimination', 'Difficulty', 'Guessing']].to_numpy()
        elif 'Dscrmn' in df_tri.columns:
            mat_tri_params = df_tri[['Dscrmn', 'Dffclt', 'Gussng']].to_numpy()
        else:
            mat_tri_params = df_tri.iloc[:, 1:4].to_numpy()

        n_min = min(mat_tri_params.shape[0], mat_respostas.shape[1])
        mat_tri_params = mat_tri_params[:n_min, :]
        v_mean = v_mean[:n_min]
        v_std = v_std[:n_min]
        v_median = v_median[:n_min]
        mat_respostas = mat_respostas[:, :n_min]

        mat_tri_params[:, 2] = np.clip(mat_tri_params[:, 2], 0, 1)
        mat_final = np.column_stack((mat_tri_params, v_mean, v_std, v_median))

        # Passa o nome do arquivo original, mas usa n_amostras_real para validação interna se necessário
        # A função draw_signoits ainda pode extrair 'tam' do nome do arquivo para fins de log/nome, 
        # mas a decisão de pular já foi feita acima.
        
        # Para garantir consistência, podemos atualizar o nome do arquivo ficticiamente 
        # ou apenas confiar na validação feita aqui. Vamos manter a chamada original,
        # mas a função draw_signoits terá uma verificação redundante (segurança).
        draw_signoits(output_dir, f_tri, mat_final, mat_respostas, ranking)
        
    print(f"\n✅ Concluído! Imagens em: {output_dir}")

if __name__ == "__main__":
    names = [str(i) for i in range(2009, 2030)]
    if len(sys.argv) < 2:
        print("Uso: python _09_matriz2graficos.py [ano]")
        sys.exit(1)
    
    for arg in sys.argv[1:]:
        if arg in names:
            genStatistics(arg)
        else:
            print(f"Ano inválido: {arg}")