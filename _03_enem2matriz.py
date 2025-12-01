import pandas as pd
import numpy as np
import sys
import os
import json
import warnings

warnings.filterwarnings("ignore")

def carregar_mapa_provas(ano):
    path = f"ENEM/{ano}/DADOS/mapa_provas.json"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def carregar_json_itens(ano):
    path_json = f"ENEM/{ano}/DADOS/ITENS_PROVA_{ano}.json"
    if os.path.exists(path_json):
        with open(path_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_microdados_path(ano):
    possibilidades = [
        f"{ano}/DADOS/MICRODADOS_ENEM_{ano}.csv",
        f"{ano}/DADOS/RESULTADOS_{ano}.csv",
    ]
    for p in possibilidades:
        if os.path.exists(p): return p
    return None

def processar_matriz(ano, amostra_alvo_str):
    amostra_alvo = int(amostra_alvo_str)
    
    print(f"--- Processando Matrizes para {ano} (Apenas _data.csv) ---")
    
    dir_saida = f"ENEM/{ano}/DADOS/MATRIZ"
    os.makedirs(dir_saida, exist_ok=True)

    # 1. Carrega Mapa de Provas (Filtro Principal)
    mapa_provas = carregar_mapa_provas(ano)
    if not mapa_provas:
        print(f"❌ Erro: mapa_provas.json não encontrado. Execute o passo 2 primeiro.")
        return

    # IDs de prova que precisamos processar (chaves do mapa)
    ids_validos = set(mapa_provas.keys())
    print(f"📋 Provas a processar: {len(ids_validos)} IDs identificados no mapa.")

    microdados_file = get_microdados_path(ano)
    if not microdados_file:
        print(f"❌ Erro: Microdados não encontrados.")
        return

    itens_json = carregar_json_itens(ano)
    
    # Colunas essenciais
    cols = ['NU_INSCRICAO', 'CO_PROVA_CN', 'CO_PROVA_CH', 'CO_PROVA_LC', 'CO_PROVA_MT',
            'TX_RESPOSTAS_CN', 'TX_RESPOSTAS_CH', 'TX_RESPOSTAS_LC', 'TX_RESPOSTAS_MT']
    
    print(f"⏳ Lendo Microdados...")
    try:
        df = pd.read_csv(microdados_file, sep=';', encoding='latin1', usecols=cols)
    except ValueError:
        df = pd.read_csv(microdados_file, sep=',', encoding='latin1', usecols=cols)
    
    areas = {'CN': 'CO_PROVA_CN', 'CH': 'CO_PROVA_CH', 'LC': 'CO_PROVA_LC', 'MT': 'CO_PROVA_MT'}
    provas_processadas = 0

    for area_sigla, col_prova in areas.items():
        col_resp = f'TX_RESPOSTAS_{area_sigla}'
        
        grupos = df.groupby(col_prova)

        for co_prova, grupo in grupos:
            co_prova_str = str(int(co_prova))
            
            # --- FILTRO: A prova está no mapa? ---
            if co_prova_str not in ids_validos:
                continue

            total_disponivel = len(grupo)
            
            # --- FILTRO: Amostra mínima ---
            if total_disponivel < amostra_alvo:
                print(f"⚠️  Prova {co_prova_str}: Amostra insuficiente ({total_disponivel} < {amostra_alvo})")
                continue

            if co_prova_str not in itens_json:
                print(f"⚠️  Prova {co_prova_str}: Metadados não encontrados no JSON de Itens.")
                continue

            dados_prova = itens_json[co_prova_str]
            cor_prova = dados_prova.get('COR', 'DESC')

            # --- PROCESSAMENTO ---
            # Garante que pegamos exatamente 'amostra_alvo' alunos
            amostra_grupo = grupo.sample(n=amostra_alvo, random_state=42)
            respostas = amostra_grupo[col_resp].dropna().tolist()

            if not respostas: continue
            
            gabarito_dict = dados_prova.get('QUESTIONS', {})
            if not gabarito_dict: continue

            # Ordena questões pelo ID da posição (1, 2, 3...)
            indices = sorted(gabarito_dict.keys(), key=lambda x: int(x))
            
            # Gera gabarito string
            gabarito_str = "".join([gabarito_dict[k]['answer'] for k in indices])
            
            # --- GERA ARQUIVO DE DADOS (0/1) ---
            matriz_binaria = []
            for resp_aluno in respostas:
                if len(resp_aluno) != len(gabarito_str): continue
                linha = [1 if r == g else 0 for r, g in zip(resp_aluno, gabarito_str)]
                matriz_binaria.append(linha)
            
            if not matriz_binaria: continue

            # Nome do arquivo usando o ID da prova e a amostra
            filename_data = f"{co_prova_str}_{amostra_alvo}_data.csv"
            path_out_data = os.path.join(dir_saida, filename_data)
            pd.DataFrame(matriz_binaria).to_csv(path_out_data, header=False, index=False)
            
            print(f"  ✅ Processada: {co_prova_str} ({cor_prova}) - {len(matriz_binaria)} alunos")
            provas_processadas += 1

    print(f"\n✅ Concluído. Total de matrizes geradas: {provas_processadas}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python _03_enem2matriz.py <ANO> <AMOSTRA>")
        sys.exit(1)
    processar_matriz(sys.argv[1], sys.argv[2])