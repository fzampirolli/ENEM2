#!/usr/bin/env python3
"""
=============================================================================
_06b_gerar_img_data.py
=============================================================================
Lê as fatias PNG em:
  ENEM/<ANO>/PROVAS_E_GABARITOS/imagens/<NOME_PROVA>/

Analisa cada fatia, aplica as regras de junção quando necessário e salva:
  ENEM/<ANO>/FIGS/<CO_PROVA>_img_data_<NNN>.png

─────────────────────────────────────────────────────────────────────────────
DIA 1  (detectado por "DIA_1" no NOME_PROVA):

  Bloco       Questão         Chave JSON
  ─────────   ──────────       ──────────
  Inglês      q1  – q5         "1"…"5"
  Espanhol    q01 – q05        "01"…"05"   (2ª ocorrência de q1)
  LC          q06 – q45        "06"…"45"
  CH          q46 – q90        "46"…"90"

DIA 2:

  Bloco       Questão       NNN       Chave JSON
  ─────────   ──────────    ───────   ──────────
  CN     q91  – q135    091–135   "91"…"135"
  MT     q136 – q180    091–180   "91"…"180"

Analisando ITENS_PROVA_ano.json:
LC 06 – 45   ==> ex. 1397_06_img_data.png
CH 46 – 90   ==> ex. 1386_51_img_data.png
CN 91 – 135  ==> ex. 1421_136_img_data.png
MT 136 – 180 ==> ex. 1409_136_img_data.png

─────────────────────────────────────────────────────────────────────────────
USO:
  python3 _06b_gerar_img_data.py <ANO> <CO_PROVA> <NOME_PROVA>

  Exemplos:
    python3 _06b_gerar_img_data.py 2024 1386 ENEM_2024_P1_CAD_04_DIA_1_VERDE
    python3 _06b_gerar_img_data.py 2024 1397 ENEM_2024_P1_CAD_08_DIA_2_VERDE
=============================================================================
"""

import sys
import os
import json
import glob
import re
from PIL import Image

# Configuração de junção (Cenário A e B do seu log)
INI_JOIN_THRESHOLD = 0.25 

def juntar_vertical(img_top, img_bot):
    w = max(img_top.width, img_bot.width)
    combined = Image.new('RGB', (w, img_top.height + img_bot.height), (255, 255, 255))
    combined.paste(img_top, (0, 0))
    combined.paste(img_bot, (0, img_top.height))
    return combined

def gerar_img_data(ano, co_prova, nome_prova):
    # Caminhos estruturados conforme a árvore do projeto
    dir_imagens = os.path.join('ENEM', ano, 'PROVAS_E_GABARITOS', 'imagens', nome_prova)
    dir_figs = os.path.join('ENEM', ano, 'FIGS')
    os.makedirs(dir_figs, exist_ok=True)

    # 1. Carrega o ranking para identificar o range da prova (ex: 91-135)
    ranking_path = os.path.join('ENEM', ano, 'DADOS', f'ranking_provas_{ano}.json')
    with open(ranking_path, 'r', encoding='utf-8') as f:
        ranking = json.load(f)
    
    info = next((r for r in ranking if r['co_prova'] == co_prova), None)
    if not info:
        return

    # Extrai o intervalo físico das questões no PDF
    start_fisico, end_fisico = map(int, info['co_posicao'].split('-'))
    is_dia_1 = 'DIA_1' in nome_prova.upper()

    # 2. Lista e ordena todas as fatias brutas
    fatias_todas = sorted(glob.glob(os.path.join(dir_imagens, "*.png")))
    
    # Pré-indexa fatias '_ini' (início da questão em outra coluna/página)
    ini_dict = {}
    for f in fatias_todas:
        if '_ini' in f:
            m = re.search(r'_q(\d+)_ini', f)
            if m: ini_dict[int(m.group(1))] = f

    # 3. Processamento com filtragem e junção
    q01_count = 0
    for fatia in fatias_todas:
        if '_ini' in fatia or '_header' in fatia: continue
        
        m = re.search(r'_q(\d+)\.png', fatia)
        if not m: continue
        q_num_pdf = int(m.group(1))

        # FILTRO: Apenas questões que pertencem a este CO_PROVA
        if not (start_fisico <= q_num_pdf <= end_fisico):
            continue

        # Lógica de mapeamento para o nome final
        if is_dia_1 and q_num_pdf == 1: q01_count += 1
        
        # Converte número do PDF para número relativo (1-45)
        q_relativa = q_num_pdf - start_fisico + 1
        
        # Define o sufixo NNN conforme o padrão do ITENS_PROVA.json
        if is_dia_1 and q_num_pdf <= 5:
            # Inglês (1º bloco) usa "1", Espanhol (2º bloco) usa "01"
            nnn = str(q_relativa) if q01_count == 1 else str(q_relativa).zfill(2)
        else:
            nnn = str(q_relativa).zfill(2)

        #dest_nome = f"{co_prova}_img_data_{nnn}.png"
        dest_nome = f"{co_prova}_{nnn}_img_data.png" # Onde nnn é "1", "01", "46", etc.
        img_principal = Image.open(fatia)

        # TRATAMENTO DE JUNÇÃO (Questões em duas colunas)
        if q_num_pdf in ini_dict:
            img_ini = Image.open(ini_dict[q_num_pdf])
            ratio = img_principal.height / img_ini.height
            
            if ratio >= INI_JOIN_THRESHOLD:
                # Caso A: Junta enunciado (ini) com alternativas (principal)
                img_final = juntar_vertical(img_ini, img_principal)
            else:
                # Caso B: O principal é apenas um cabeçalho, usa apenas o ini
                img_final = img_ini
        else:
            img_final = img_principal

        img_final.save(os.path.join(dir_figs, dest_nome), 'PNG')

if __name__ == "__main__":
    # Garante que os argumentos com espaços sejam lidos corretamente
    gerar_img_data(sys.argv[1], sys.argv[2], sys.argv[3])