'''
==============================================================================
CONVENÇÃO DE NOMES — IMAGENS EM ENEM/<ANO>/FIGS/
==============================================================================

  Bloco            q_id (chave JSON)      NNN no arquivo
  ─────────────    ─────────────────      ───────────────
  Inglês  (D1)     "1" … "5"             1 … 5
  Espanhol (D1)    "01" … "05"           01 … 05
  LC (D1)          "06" … "09"           06 … 09
  LC (D1)          "10" … "50"           10 … 50
  CH (D1)          "51" … "90"           51 … 90
  CN+MT (D2)       "91" … "180"          91 … 180
==============================================================================
'''

import json
import sys
import pandas as pd
import os

# Configuração da estrutura base da questão no JSON com campo idioma
qstr = '{"answer": "__answer__", "ability": __ability__, "id": __id__, "percentage": 0, "irt": [], "images": [], "videos": [], "subareas": [], "idioma": "__idioma__" }'

def carregar_top_provas(ano, top_n):
    """
    Lê o ranking e identifica os códigos das provas associados aos TOP N arquivos PDF por dia.
    """
    path_ranking = f'ENEM/{ano}/DADOS/ranking_provas_{ano}.json'
    if not os.path.exists(path_ranking):
        print(f"❌ Erro: Ranking não encontrado em {path_ranking}")
        return set(), {}

    with open(path_ranking, 'r', encoding='utf-8') as f:
        ranking = json.load(f)

    selected_pdfs = []
    for dia in ["1", "2"]:
        # Filtra por dia e ordena por total de alunos (descrescente)
        cadernos_dia = [r for r in ranking if r['dia'] == dia and r['arquivo_pdf'] != "NÃO ENCONTRADO"]
        
        vistos = set()
        pdfs_unicos = []
        for c in cadernos_dia:
            if c['arquivo_pdf'] not in vistos:
                pdfs_unicos.append(c['arquivo_pdf'])
                vistos.add(c['arquivo_pdf'])
            if len(pdfs_unicos) == top_n:
                break
        selected_pdfs.extend(pdfs_unicos)

    co_provas_top = {str(r['co_prova']) for r in ranking if r['arquivo_pdf'] in selected_pdfs}
    ranking_map = {str(r['co_prova']): r for r in ranking if str(r['co_prova']) in co_provas_top}
    
    return co_provas_top, ranking_map

def processar_gabarito(ano, top_n):
    # Ajuste de caminho para consistência com o projeto
    csv_path = f'ENEM/{ano}/DADOS/ITENS_PROVA_{ano}.csv'
    mapa_path = f'ENEM/{ano}/DADOS/mapa_provas.json'
    
    if not os.path.exists(csv_path):
        # Tenta caminho alternativo sem prefixo ENEM se necessário
        csv_path_alt = f'{ano}/DADOS/ITENS_PROVA_{ano}.csv'
        if os.path.exists(csv_path_alt):
            csv_path = csv_path_alt
        else:
            print(f"❌ Erro: CSV não encontrado em {csv_path}")
            return

    co_provas_alvo, info_ranking = carregar_top_provas(ano, top_n)
    
    try:
        with open(mapa_path, 'r', encoding='utf-8') as f:
            mapa_tipos = json.load(f)
    except:
        mapa_tipos = {}

    try:
        df = pd.read_csv(csv_path, sep=';', encoding='latin1')
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return

    gab_dict = {}
    df_top = df[df['CO_PROVA'].astype(str).isin(co_provas_alvo)].copy()

    for co_prova_int in df_top['CO_PROVA'].unique():
        co_prova = str(int(co_prova_int))
        df_aux = df_top[df_top['CO_PROVA'] == co_prova_int].sort_values('CO_POSICAO')
        
        q_ing = {}
        q_others = {}
        
        for _, row in df_aux.iterrows():
            pos = int(row['CO_POSICAO'])
            lang = row['TP_LINGUA'] # 0: Inglês, 1: Espanhol
            
            # --- DETERMINAÇÃO DE IDIOMA E CHAVE ---
            idioma = "português"
            chave_json = ""
            
            if pos <= 5:
                if lang == 0:
                    idioma = "inglês"
                    chave_json = str(pos) # "1"..."5"
                elif lang == 1:
                    idioma = "espanhol"
                    chave_json = str(pos).zfill(2) # "01"..."05"
            else:
                chave_json = str(pos).zfill(2) if pos < 100 else str(pos) # "06"..."180"

            item_id = str(int(row['CO_ITEM']))
            hab_val = str(int(row['CO_HABILIDADE'])) if pd.notna(row['CO_HABILIDADE']) else "null"
            
            item_obj = json.loads(
                qstr.replace('__answer__', str(row['TX_GABARITO']))
                    .replace('__ability__', hab_val)
                    .replace('__id__', item_id)
                    .replace('__idioma__', idioma)
            )
            
            if idioma == "inglês":
                q_ing[chave_json] = item_obj
            else:
                q_others[chave_json] = item_obj

        # ORDENAÇÃO: Inglês primeiro, depois os outros (incluindo Espanhol 01-05)
        questions_dict = {}
        # Garante ordem 1, 2, 3, 4, 5
        for k in sorted(q_ing.keys(), key=int):
            questions_dict[k] = q_ing[k]
        # Garante ordem 01, 02... 180
        for k in sorted(q_others.keys(), key=lambda x: int(x)):
            questions_dict[k] = q_others[k]

        info = info_ranking.get(co_prova, {})
        gab_dict[co_prova] = {
            'COR': str(df_aux['TX_COR'].iloc[0]).upper().replace('BRANCA', 'BRANCO').replace('AMARELA', 'AMARELO'),
            "AREA": str(df_aux['SG_AREA'].iloc[0]),
            "PROOF_TYPE": mapa_tipos.get(co_prova, co_prova),
            "DIA": str(info.get('dia', "ND")),
            "CO_POSICAO": info.get('co_posicao', "ND"),
            "TOTAL_ALUNOS": info.get('total_alunos', 0),
            "APLICACAO": info.get('aplicacao', "ND"),
            "ARQUIVO_PDF": info.get('arquivo_pdf', ""),
            "QUESTIONS": questions_dict
        }

    output_path = f'ENEM/{ano}/DADOS/ITENS_PROVA_{ano}.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(gab_dict, f, indent=4, ensure_ascii=False)
    
    print(f"✅ JSON gerado: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python _02b_csv2json.py <ANO> <TOP>")
        sys.exit(1)

    processar_gabarito(sys.argv[1], int(sys.argv[2]))