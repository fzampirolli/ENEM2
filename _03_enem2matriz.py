import pandas as pd
import numpy as np
import sys
import os
import glob
import json
import re

def carregar_json_itens(ano):
    # Tenta carregar o JSON de itens para pegar COR e AREA
    path_json = f"ENEM/{ano}/DADOS/ITENS_PROVA_{ano}.json"
    if os.path.exists(path_json):
        with open(path_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_microdados_path(ano):
    possibilidades = [
        f"{ano}/DADOS/MICRODADOS_ENEM_{ano}.csv",
        f"MICRODADOS_ENEM_{ano}.csv"
    ]
    for p in possibilidades:
        if os.path.exists(p): return p
    return None

def listar_pdfs_existentes(ano):
    """
    Retorna uma string única contendo os nomes de todos os PDFs na pasta.
    Usada para verificar se uma prova (ex: AZUL) existe fisicamente.
    """
    path_pdfs = f"{ano}/PROVAS E GABARITOS/*.pdf"
    arquivos = glob.glob(path_pdfs)
    # Retorna nomes em uppercase para facilitar a busca
    return " ".join([os.path.basename(f).upper() for f in arquivos])

def processar_matriz(ano, amostra_alvo_str):
    amostra_alvo = int(amostra_alvo_str)
    
    print(f"--- Processando Matrizes para {ano} ---")
    print(f"--- Critério: Mínimo de {amostra_alvo} alunos por prova ---")

    dir_saida = f"ENEM/{ano}/DADOS/MATRIZ"
    if not os.path.exists(dir_saida):
        os.makedirs(dir_saida, exist_ok=True)

    microdados_file = get_microdados_path(ano)
    if not microdados_file:
        print(f"❌ Erro: Microdados não encontrados para {ano}")
        return

    itens_json = carregar_json_itens(ano)
    pdfs_existentes = listar_pdfs_existentes(ano) # [NOVO] Carrega lista de PDFs

    print(f"PDFs encontrados na pasta: \n   {pdfs_existentes[:100]}...") 
    
    # Colunas essenciais para economizar memória
    cols = ['NU_INSCRICAO', 'CO_PROVA_CN', 'CO_PROVA_CH', 'CO_PROVA_LC', 'CO_PROVA_MT',
            'TX_RESPOSTAS_CN', 'TX_RESPOSTAS_CH', 'TX_RESPOSTAS_LC', 'TX_RESPOSTAS_MT']
    
    print(f"Lendo Microdados COMPLETO: {microdados_file} ...")
    
    try:
        df = pd.read_csv(microdados_file, sep=';', encoding='latin1', usecols=cols)
    except ValueError:
        df = pd.read_csv(microdados_file, sep=',', encoding='latin1', usecols=cols)
    
    print(f"Dataset carregado: {len(df)} registros totais.")

    areas = {
        'CN': 'CO_PROVA_CN',
        'CH': 'CO_PROVA_CH',
        'LC': 'CO_PROVA_LC',
        'MT': 'CO_PROVA_MT'
    }

    provas_processadas = 0
    relatorio_provas = [] 

    for area_sigla, col_prova in areas.items():
        col_resp = f'TX_RESPOSTAS_{area_sigla}'
        
        grupos = df.groupby(col_prova)

        for co_prova, grupo in grupos:
            co_prova_str = str(int(co_prova))
            total_disponivel = len(grupo)
            
            # Pega metadados
            cor_prova = "DESCONHECIDA"
            if co_prova_str in itens_json:
                cor_prova = itens_json[co_prova_str].get('COR', 'DESC').upper()
            
            relatorio_provas.append({
                'id': co_prova_str,
                'cor': cor_prova,
                'area': area_sigla,
                'qtd': total_disponivel
            })

            # --- FILTRO 1: AMOSTRA MÍNIMA ---
            if total_disponivel < amostra_alvo:
                continue

            # --- FILTRO 2: EXISTÊNCIA DO PDF [NOVO] ---
            # Verifica se a cor desta prova existe nos nomes dos PDFs
            # Ex: Se cor_prova="AZUL", verifica se "AZUL" está nos nomes dos arquivos
            # Exceção para "BRANCA"/"BRANCO" e "AMARELA"/"AMARELO"
            match_pdf = False
            
            termo_busca = cor_prova
            if termo_busca == "BRANCA": termo_busca = "BRANCO"
            if termo_busca == "AMARELA": termo_busca = "AMARELO"

            # Se a cor da prova não estiver na string dos PDFs, ignoramos
            # Isso evita processar 'Laranja' (Ledor) se não tiver o PDF Laranja
            if termo_busca in pdfs_existentes:
                 match_pdf = True
            
            if not match_pdf:
                # print(f"  [Ignorado] Prova {co_prova_str} ({cor_prova}) - PDF não encontrado na pasta.")
                continue

            # --- PROCESSAMENTO ---
            amostra_grupo = grupo.sample(n=amostra_alvo, random_state=42)
            respostas = amostra_grupo[col_resp].dropna().tolist()

            if not respostas: continue

            if co_prova_str not in itens_json:
                continue

            gabarito_dict = itens_json[co_prova_str].get('QUESTIONS', {})
            if not gabarito_dict: continue

            indices = sorted(gabarito_dict.keys(), key=lambda x: int(x))
            gabarito_str = "".join([gabarito_dict[k]['answer'] for k in indices])
            
            matriz_binaria = []
            for resp_aluno in respostas:
                if len(resp_aluno) != len(gabarito_str): continue
                linha = []
                for r, g in zip(resp_aluno, gabarito_str):
                    linha.append(1 if r == g else 0)
                matriz_binaria.append(linha)
            
            if not matriz_binaria: continue

            filename = f"{co_prova_str}_{amostra_alvo}_data.csv"
            path_out = os.path.join(dir_saida, filename)
            
            pd.DataFrame(matriz_binaria).to_csv(path_out, header=False, index=False)
            print(f"  ✅ Gerada matriz: {filename} ({len(matriz_binaria)} alunos) - Cor: {cor_prova} [{area_sigla}]")
            provas_processadas += 1

    print(f"\n{'='*60}")
    print(f"RESUMO DAS PROVAS (> {amostra_alvo} alunos & PDF Existente)")
    print(f"{'ID':<6} | {'AREA':<4} | {'COR':<10} | {'QTD TOTAL':<10} | {'STATUS'}")
    print(f"{'-'*6} | {'-'*4} | {'-'*10} | {'-'*10} | {'-'*10}")
    
    relatorio_provas.sort(key=lambda x: x['qtd'], reverse=True)
    
    provas_validas = 0
    for p in relatorio_provas:
        # Recalcula validação para o relatório visual
        termo_busca = p['cor']
        if termo_busca == "BRANCA": termo_busca = "BRANCO"
        if termo_busca == "AMARELA": termo_busca = "AMARELO"
        
        tem_pdf = termo_busca in pdfs_existentes
        tem_amostra = p['qtd'] >= amostra_alvo
        
        status = "❌ Ignorada"
        if tem_amostra and tem_pdf:
            status = "✅ Processada"
            provas_validas += 1
            print(f"{p['id']:<6} | {p['area']:<4} | {p['cor']:<10} | {p['qtd']:<10} | {status}")
        elif not tem_pdf and tem_amostra:
             # Mostra as que tinham amostra mas não tinham PDF (importante para debug)
             status = "⚠️  Sem PDF"
             print(f"{p['id']:<6} | {p['area']:<4} | {p['cor']:<10} | {p['qtd']:<10} | {status}")

    print(f"{'-'*60}")
    print(f"Total de matrizes geradas: {provas_processadas}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python _03_enem2matriz.py <ANO> <AMOSTRA>")
        sys.exit(1)
    processar_matriz(sys.argv[1], sys.argv[2])