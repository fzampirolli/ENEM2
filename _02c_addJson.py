'''
=====================================================================
Copyright (C) 2021 UFABC, developed by Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of "ENEM Interativo".

Languages: Python 3.8.5, Javascript, HTML and many libraries
described at github.com/fzampirolli/ENEM
=====================================================================
'''

import json
import sys
import os

def alteraChave0(ano, amostra_raw):
  CHAVE = 'images'
  
  # Formata a amostra para 6 dígitos (ex: 10000 -> "010000")
  amostra_str = str(amostra_raw).zfill(6)
  
  # --- CORREÇÃO: Agora aponta para a pasta de destino ENEM/ANO/DADOS ---
  arquivo_json = os.path.join('ENEM', ano, 'DADOS', f'ITENS_PROVA_{ano}.json')

  # Fallback: Se não achar na pasta ENEM, tenta na pasta original (retrocompatibilidade)
  if not os.path.exists(arquivo_json):
      arquivo_legacy = os.path.join(ano, 'DADOS', f'ITENS_PROVA_{ano}.json')
      if os.path.exists(arquivo_legacy):
          print(f"⚠️  Aviso: JSON não encontrado em {arquivo_json}. Usando legado: {arquivo_legacy}")
          arquivo_json = arquivo_legacy
      else:
          print(f"❌ Arquivo não encontrado: {arquivo_json}")
          return

  print(f"Processando {ano} com amostra {amostra_str} em: {arquivo_json}")

  with open(arquivo_json, 'r', encoding='utf-8') as f:
    data = json.load(f)
    
    for i, t in enumerate(data.keys()):
      # Limpa a lista de imagens na primeira questão para evitar duplicação em execuções repetidas
      first_q = list(data[t]['QUESTIONS'].keys())[0]
      if CHAVE in data[t]['QUESTIONS'][first_q]:
          data[t]['QUESTIONS'][first_q][CHAVE] = [] 
      
      for q in data[t]['QUESTIONS']:
        # Garante que a chave 'images' é uma lista vazia antes de dar append
        data[t]['QUESTIONS'][q][CHAVE] = []
        
        # Constrói o nome do arquivo usando a amostra dinâmica
        # Ex: 505_010000_fig_tri_001.png
        f_tri = f"{t}_{amostra_str}_fig_tri_{str(int(q)).zfill(3)}.png"
        data[t]['QUESTIONS'][q][CHAVE].append(f_tri)
        
        f_box = f"{t}_{amostra_str}_fig_box_{str(int(q)).zfill(3)}.png"
        data[t]['QUESTIONS'][q][CHAVE].append(f_box)

  with open(arquivo_json, 'w', encoding='utf-8') as outfile:
    json.dump(data, outfile, indent=2, ensure_ascii=False)
    print(f"✅ JSON atualizado com chaves de imagem: {arquivo_json}")


def alteraChave(ano, amostra_raw):
    CHAVE = 'images'
    amostra_str = str(amostra_raw).zfill(6) # Ex: 000100
    
    arquivo_json = os.path.join('ENEM', ano, 'DADOS', f'ITENS_PROVA_{ano}.json')
    caminho_mapa = os.path.join('ENEM', ano, 'DADOS', 'mapa_provas.json')

    if not os.path.exists(arquivo_json) or not os.path.exists(caminho_mapa):
        print("❌ Arquivos de dados ou mapa não encontrados.")
        return

    with open(arquivo_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(caminho_mapa, 'r', encoding='utf-8') as f:
        mapa = json.load(f)

    # Percorre cada prova no JSON de itens
    for co_prova in data: # co_prova é "1068"
        questions = data[co_prova].get('QUESTIONS', {})
        for q_id in questions:
            questions[q_id]['images'] = []
            num_q = str(int(q_id)).zfill(3)
            
            # USAR O ID INDIVIDUAL (co_prova)
            f_tri = f"{co_prova}_{amostra_str}_fig_tri_{num_q}.png"
            f_box = f"{co_prova}_{amostra_str}_fig_box_{num_q}.png"
            
            questions[q_id]['images'].append(f_tri)
            questions[q_id]['images'].append(f_box)

    with open(arquivo_json, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)
    

# --- BLOCO PRINCIPAL ---
if __name__ == "__main__":
    # Lista de anos suportados
    anos_validos = [str(i) for i in range(2009, 2030)]
    
    amostra_detectada = "10000" 
    anos_para_processar = []

    for arg in sys.argv[1:]:
        if arg in anos_validos:
            anos_para_processar.append(arg)
        elif arg.isdigit():
            amostra_detectada = arg

    if not anos_para_processar:
        print("Uso: python _03_addJson.py <ANO> [AMOSTRA]")
        print("Exemplo: python _03_addJson.py 2024 10000")
    else:
        for ano in anos_para_processar:
            alteraChave(ano, amostra_detectada)