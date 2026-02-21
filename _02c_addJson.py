'''
=====================================================================
Copyright (C) 2021 UFABC, developed by Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of "ENEM Interativo".

Languages: Python 3.8.5, Javascript, HTML and many libraries
described at github.com/fzampirolli/ENEM

==============================================================================
CONVENÇÃO DE NOMES — IMAGENS EM ENEM/<ANO>/FIGS/
==============================================================================

 <CO_PROVA>_<NNN>_fig_box_<AMOSTRA>.png   ← boxplot     (varia por amostra)
 <CO_PROVA>_<NNN>_fig_tri_<AMOSTRA>.png   ← curva TRI   (varia por amostra)
 <CO_PROVA>_<NNN>_img_data.png            ← fatia prova (independe de amostra)
 <CO_PROVA>_<NNN>_help.html               ← ajuda contextual (independe de amostra)

NNN é exatamente a chave q_id do JSON:

  Bloco            q_id (chave JSON)      NNN no arquivo
  ─────────────    ─────────────────      ───────────────
  Inglês  (D1)     "1" … "5"             1 … 5
  Espanhol (D1)    "01" … "05"           01 … 05
  LC (D1)          "06" … "09"           06 … 09
  LC (D1)          "10" … "50"           10 … 50
  CH (D1)          "51" … "90"           51 … 90
  CN+MT (D2)       "91" … "180"          91 … 180

A geração física de fig_data é feita por _06b_gerar_fig_data.py.
Este script apenas registra os nomes no JSON.
==============================================================================
'''

import json
import sys
import os

def alteraChave(ano, amostra_raw):
    CHAVE = 'images'
    amostra_str = str(amostra_raw).zfill(6) # Ex: 000100
    
    arquivo_json = os.path.join('ENEM', ano, 'DADOS', f'ITENS_PROVA_{ano}.json')

    if not os.path.exists(arquivo_json):
        print(f"❌ Arquivo de dados não encontrado em: {arquivo_json}")
        return

    print(f"Processando {ano} com amostra {amostra_str} em: {arquivo_json}")

    with open(arquivo_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Percorre cada prova no JSON de itens
    for co_prova in data:
        questions = data[co_prova].get('QUESTIONS', {})
        for q_id in questions:
            # Limpa a lista para evitar duplicações em re-execuções
            questions[q_id][CHAVE] = []
            
            # NNN agora segue EXATAMENTE a chave q_id (ex: "1", "01", "91")
            nnn = q_id 
            
            # Montagem dos nomes seguindo a nova convenção: <CO_PROVA>_<NNN>_fig_...
            f_tri  = f"{co_prova}_{nnn}_fig_tri_{amostra_str}.png"
            f_box  = f"{co_prova}_{nnn}_fig_box_{amostra_str}.png"
            f_data = f"{co_prova}_{nnn}_img_data.png"
            f_help = f"{co_prova}_{nnn}_help.html"

            # Ordem padrão: [TRI, Boxplot, Imagem da Questão]
            questions[q_id][CHAVE].append(f_tri)
            questions[q_id][CHAVE].append(f_box)
            questions[q_id][CHAVE].append(f_data)
            questions[q_id][CHAVE].append(f_help)


    with open(arquivo_json, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON atualizado com sucesso!")

# --- BLOCO PRINCIPAL ---
if __name__ == "__main__":
    # Lista de anos suportados
    anos_validos = [str(i) for i in range(2009, 2030)]
    
    amostra_detectada = "10000" 
    anos_para_processar = []

    # Parsing simples de argumentos
    for arg in sys.argv[1:]:
        if arg in anos_validos:
            anos_para_processar.append(arg)
        elif arg.isdigit():
            amostra_detectada = arg

    if not anos_para_processar:
        print("Uso: python _02c_addJson.py <ANO> [AMOSTRA]")
        print("Exemplo: python _02c_addJson.py 2024 10000")
    else:
        for ano in anos_para_processar:
            alteraChave(ano, amostra_detectada)