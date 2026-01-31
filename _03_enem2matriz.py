import pandas as pd
import numpy as np
import sys
import os
import json
import warnings

# Silencia avisos de performance do pandas
warnings.filterwarnings("ignore")

def buscar_path_microdados(ano):
    """Procura o ficheiro de dados usando os padrões antigo e novo"""
    dados_dir = os.path.join(ano, "DADOS")
    nomes_possiveis = [
        f"MICRODADOS_ENEM_{ano}.csv",
        f"RESULTADOS_{ano}.csv"
    ]
    
    for nome in nomes_possiveis:
        caminho = os.path.join(dados_dir, nome)
        if os.path.exists(caminho):
            return caminho
    return None

def carregar_mapa_provas(ano):
    """Carrega o mapa para saber quais IDs são o 'Top N'"""
    path = os.path.join("ENEM", ano, "DADOS", "mapa_provas.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def carregar_ranking(ano):
    """Carrega o ranking para validar se os IDs existem e são voados."""
    path = os.path.join("ENEM", ano, "DADOS", f"ranking_provas_{ano}.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            # Transforma em dicionário indexado pelo co_prova para busca rápida
            return {str(item['co_prova']): item for item in json.load(f)}
    return {}

def processar_matriz(ano, amostra_alvo_str):
    amostra_alvo = int(amostra_alvo_str)
    amostra_formatada = str(amostra_alvo).zfill(6)
    
    print(f"--- Gerando Matrizes Top N para {ano} (Amostra: {amostra_formatada}) ---")
    
    # 1. Obter os IDs Alvo e Validar no Ranking
    mapa = carregar_mapa_provas(ano)
    ranking = carregar_ranking(ano)
    
    if not mapa:
        print(f"❌ mapa_provas.json não encontrado. Rode a Etapa 02a primeiro.")
        return
    
    target_ids = set(mapa.keys())
    print(f"🎯 IDs Selecionados via Mapa: {', '.join(sorted(target_ids))}")
    
    # Validação contra o Ranking
    ids_validados = []
    for pid in sorted(target_ids):
        if pid in ranking:
            info = ranking[pid]
            print(f"   [VALIDADO] ID {pid}: {info.get('tx_cor','')} {info.get('sg_area','')} - {info.get('total_alunos',0)} alunos")
            ids_validados.append(pid)
        else:
            print(f"   [AVISO] ID {pid} não encontrado no arquivo de ranking!")
    
    # 2. Carregar Gabaritos e Microdados
    path_itens_csv = os.path.join(ano, "DADOS", f"ITENS_PROVA_{ano}.csv")
    df_itens_all = pd.read_csv(path_itens_csv, sep=';', encoding='latin1')

    # path_microdados = os.path.join(ano, "DADOS", f"MICRODADOS_ENEM_{ano}.csv")
    # if not os.path.exists(path_microdados):
    #     print(f"❌ Microdados não encontrados em: {path_microdados}")
    #     return
    
    # 1. Localizar ficheiro de microdados
    path_microdados = buscar_path_microdados(ano)
    if not path_microdados:
        print(f"❌ Erro: Microdados não encontrados para o ano {ano}.")
        return

    print(f"--- Gerando Matrizes para {ano} (Ficheiro: {os.path.basename(path_microdados)}) ---")

    # 3. Preparar Coleta e Saída
    dir_saida = os.path.join("ENEM", ano, "DADOS", "MATRIZ") # Salva direto na DADOS do ano
    amostras_coletadas = {pid: [] for pid in ids_validados}
    cols_leitura = ['CO_PROVA_CN', 'CO_PROVA_CH', 'CO_PROVA_LC', 'CO_PROVA_MT',
                    'TX_RESPOSTAS_CN', 'TX_RESPOSTAS_CH', 'TX_RESPOSTAS_LC', 'TX_RESPOSTAS_MT']

    print(f"⏳ Lendo Microdados e filtrando alunos...")
    chunks = pd.read_csv(path_microdados, sep=';', encoding='latin1', usecols=cols_leitura, chunksize=100000)
    
    for chunk in chunks:
        if all(len(amostras_coletadas[pid]) >= amostra_alvo for pid in ids_validados):
            break
            
        for area in ['CN', 'CH', 'LC', 'MT']:
            col_prova = f'CO_PROVA_{area}'
            col_resp = f'TX_RESPOSTAS_{area}'
            
            chunk[col_prova] = pd.to_numeric(chunk[col_prova], errors='coerce').fillna(-1).astype(int).astype(str)
            
            for pid in ids_validados:
                if len(amostras_coletadas[pid]) >= amostra_alvo: continue
                
                mask = chunk[col_prova] == pid
                resps = chunk.loc[mask, col_resp].dropna().tolist()
                
                vagas = amostra_alvo - len(amostras_coletadas[pid])
                amostras_coletadas[pid].extend(resps[:vagas])

    # 4. Salvar Matrizes Binárias
    os.makedirs(dir_saida, exist_ok=True)
    provas_ok = 0
    for pid, resps in amostras_coletadas.items():
        filename = f"{pid}_{amostra_formatada}_data.csv"
        path_out = os.path.join(dir_saida, filename)

        if len(resps) < amostra_alvo:
            print(f"⚠️ Prova {pid}: Amostra insuficiente ({len(resps)}/{amostra_alvo})")
            if len(resps) == 0: continue
            
        df_gab = df_itens_all[df_itens_all['CO_PROVA'].astype(int).astype(str) == pid].sort_values('CO_POSICAO')
        gabarito_str = "".join(df_gab['TX_GABARITO'].astype(str).tolist())
        
        if not gabarito_str: continue

        matriz = [[1 if a == b else 0 for a, b in zip(r, gabarito_str)] for r in resps]
        pd.DataFrame(matriz).to_csv(path_out, header=False, index=False)
        print(f"  ✅ Matriz criada: {filename} ({len(resps)} alunos)")
        provas_ok += 1

    print(f"\n✨ Processo finalizado. {provas_ok} matrizes salvas em {dir_saida}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python _03_enem2matriz.py <ANO> <AMOSTRA>")
    else:
        processar_matriz(sys.argv[1], sys.argv[2])