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
#!/usr/bin/env python3
import sys
import os
import json
import glob
import re
from PIL import Image

INI_JOIN_THRESHOLD = 0.25 

def juntar_vertical(img_top, img_bot):
    w = max(img_top.width, img_bot.width)
    combined = Image.new('RGB', (w, img_top.height + img_bot.height), (255, 255, 255))
    combined.paste(img_top, (0, 0))
    combined.paste(img_bot, (0, img_top.height))
    return combined

def gerar_img_data(ano, co_prova, nome_prova):
    dir_imagens = os.path.join('ENEM', ano, 'PROVAS_E_GABARITOS', 'imagens', nome_prova)
    dir_figs = os.path.join('ENEM', ano, 'FIGS')
    os.makedirs(dir_figs, exist_ok=True)

    ranking_path = os.path.join('ENEM', ano, 'DADOS', f'ranking_provas_{ano}.json')
    with open(ranking_path, 'r', encoding='utf-8') as f:
        ranking = json.load(f)
    
    info = next((r for r in ranking if r['co_prova'] == co_prova), None)
    if not info: return

    area = info.get('sg_area', '')
    start_fisico, end_fisico = map(int, info['co_posicao'].split('-'))

    # Ordenação rigorosa pelos prefixos numéricos (001, 002...) garante a ordem do PDF
    fatias_todas = sorted(glob.glob(os.path.join(dir_imagens, "*.png")))
    
    # --- CORREÇÃO: Mapeamento de Enunciados (INI) por Idioma ---
    ini_dict = {}
    q01_ini_discovery_count = 0
    
    for f in fatias_todas:
        if '_ini' in f:
            m = re.search(r'_q(\d+)_ini', f)
            if m:
                q_num = int(m.group(1))
                if q_num <= 5:
                    q01_ini_discovery_count += 1
                    # Se for as 5 primeiras ocorrências de q1-5, armazena como Inglês
                    # Se for da 6ª em diante, armazena como Espanhol
                    prefixo = "ING" if q01_ini_discovery_count <= 5 else "ESP"
                    ini_dict[f"{prefixo}_{q_num}"] = f
                else:
                    ini_dict[q_num] = f

    q01_process_count = 0
    for fatia in fatias_todas:
        if '_ini' in fatia or '_header' in fatia: continue
        m = re.search(r'_q(\d+)\.png', fatia)
        if not m: continue
        
        q_num_pdf = int(m.group(1))

        if not (start_fisico <= q_num_pdf <= end_fisico):
            continue

        # --- LÓGICA DE NNN E VÍNCULO DE IDIOMA ---
        fatia_ini_path = None

        if area == 'LC':
            if q_num_pdf <= 5:
                q01_process_count += 1
                if q01_process_count <= 5:
                    # Bloco Inglês
                    nnn = str(q_num_pdf)
                    fatia_ini_path = ini_dict.get(f"ING_{q_num_pdf}")
                else:
                    # Bloco Espanhol
                    nnn = str(q_num_pdf).zfill(2)
                    fatia_ini_path = ini_dict.get(f"ESP_{q_num_pdf}")
            else:
                nnn = str(q_num_pdf).zfill(2)
                fatia_ini_path = ini_dict.get(q_num_pdf)
        
        elif area == 'CH':
            nnn = str(q_num_pdf) # Chaves 46-90 no JSON
            fatia_ini_path = ini_dict.get(q_num_pdf)
            
        else: # CN e MT
            nnn = str(q_num_pdf)
            fatia_ini_path = ini_dict.get(q_num_pdf)

        dest_nome = f"{co_prova}_{nnn}_img_data.png"
        img_principal = Image.open(fatia)

        # --- CORREÇÃO: Junção usando o INI do idioma correto ---
        if fatia_ini_path:
            img_ini = Image.open(fatia_ini_path)
            ratio = img_principal.height / img_ini.height
            # Se a imagem principal for muito pequena (ex: informativo de idioma),
            # ou se for uma questão normal com enunciado separado, junta.
            img_final = juntar_vertical(img_ini, img_principal) if ratio >= INI_JOIN_THRESHOLD else img_ini
        else:
            img_final = img_principal

        img_final.save(os.path.join(dir_figs, dest_nome), 'PNG')
        print(f"✅ Salvo: {dest_nome} (Base: {os.path.basename(fatia)})")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        gerar_img_data(sys.argv[1], sys.argv[2], sys.argv[3])