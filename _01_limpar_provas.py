'''
=====================================================================
Script de Limpeza de Provas do ENEM (Top N por Amostra)
Uso: python _01_limpar_provas.py <ANO> <TOP>

Lógica: 
  1. Identifica amostra de alunos por Cor/Dia nos microdados.
  2. Lista todos os PDFs disponíveis.
  3. Pontua cada PDF com base na amostra da sua cor.
  4. Mantém apenas os TOP PDFs com maior pontuação para Dia 1 e Dia 2.
  5. Remove gabaritos e arquivos especiais automaticamente.
=====================================================================
'''

import os
import sys
import glob
import json
import pandas as pd
import warnings

# Suprime avisos do pandas
warnings.filterwarnings("ignore")

def carregar_json_itens(ano):
    caminhos = [
        os.path.join("ENEM", ano, "DADOS", f"ITENS_PROVA_{ano}.json"),
        os.path.join(ano, "DADOS", f"ITENS_PROVA_{ano}.json")
    ]
    for path in caminhos:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
    return None

def get_microdados_path(ano):
    caminhos = [
        os.path.join(ano, "DADOS", f"MICRODADOS_ENEM_{ano}.csv"),
        f"MICRODADOS_ENEM_{ano}.csv"
    ]
    for path in caminhos:
        if os.path.exists(path): return path
    return None

def obter_amostra_por_cor(ano):
    """
    Retorna dicionário: 
    { 
      '1': {'AZUL': 5000, 'AMARELA': 4000}, 
      '2': {'CINZA': 5000...} 
    }
    """
    csv_path = get_microdados_path(ano)
    json_itens = carregar_json_itens(ano)

    amostra_por_cor = {'1': {}, '2': {}}

    if not csv_path or not json_itens:
        print("⚠️  Dados insuficientes para ranking amostral.")
        return None

    print(f"   ⏳ Lendo Microdados para ranking: {csv_path} ...")
    
    cols_d1 = ['CO_PROVA_LC', 'CO_PROVA_CH'] 
    cols_d2 = ['CO_PROVA_CN', 'CO_PROVA_MT']
    
    try:
        df = pd.read_csv(csv_path, sep=';', encoding='latin1', usecols=cols_d1 + cols_d2)
    except ValueError:
        df = pd.read_csv(csv_path, sep=',', encoding='latin1', usecols=cols_d1 + cols_d2)

    # Mapeamento ID -> Cor
    id_to_color = {}
    for pid, dados in json_itens.items():
        cor = dados.get('COR', '').upper()
        if cor == "BRANCA": cor = "BRANCO"
        if cor == "AMARELA": cor = "AMARELO"
        id_to_color[pid] = cor

    # Processa Dia 1 (Soma LC e CH)
    for col in cols_d1:
        counts = df[col].value_counts().to_dict()
        for pid, qtd in counts.items():
            cor = id_to_color.get(str(int(pid)), 'DESCONHECIDA')
            if cor != 'DESCONHECIDA':
                amostra_por_cor['1'][cor] = amostra_por_cor['1'].get(cor, 0) + qtd

    # Processa Dia 2 (Soma CN e MT)
    for col in cols_d2:
        counts = df[col].value_counts().to_dict()
        for pid, qtd in counts.items():
            cor = id_to_color.get(str(int(pid)), 'DESCONHECIDA')
            if cor != 'DESCONHECIDA':
                amostra_por_cor['2'][cor] = amostra_por_cor['2'].get(cor, 0) + qtd

    # Exibe Ranking
    for dia in ['1', '2']:
        print(f"   📊 Ranking Amostral Dia {dia}:")
        rank = sorted(amostra_por_cor[dia].items(), key=lambda x: x[1], reverse=True)
        for cor, qtd in rank:
            print(f"      - {cor}: {qtd:,} alunos")

    return amostra_por_cor

def identificar_pdf(filename):
    """Extrai dia, cor e prioridade do nome do arquivo."""
    name_upper = filename.upper()
    
    # Identifica Dia
    dia = "0"
    if "DIA_1" in name_upper or "DIA 1" in name_upper or "_D1" in name_upper: 
        dia = "1"
    elif "DIA_2" in name_upper or "DIA 2" in name_upper or "_D2" in name_upper: 
        dia = "2"
    
    # Identifica Cor
    cores_comuns = ["AZUL", "AMARELO", "AMARELA", "BRANCO", "BRANCA", "ROSA", "CINZA", "LARANJA", "VERDE"]
    cor_arquivo = "DESCONHECIDA"
    for c in cores_comuns:
        if c in name_upper:
            cor_arquivo = c
            if c == "BRANCA": cor_arquivo = "BRANCO"
            if c == "AMARELA": cor_arquivo = "AMARELO"
            break
            
    # Prioridade (Desempate): Provas regulares > Digitais > Especiais
    prioridade = 10
    if "DIGITAL" in name_upper: prioridade = 5
    if "LIBRAS" in name_upper or "LEDOR" in name_upper or "AMPLIADA" in name_upper: prioridade = 1

    return dia, cor_arquivo, prioridade

def limpar_diretorio(ano, top_n):
    dir_path = os.path.join(ano, "PROVAS E GABARITOS")
    
    if not os.path.exists(dir_path):
        print(f"❌ Erro: Diretório não encontrado: {dir_path}")
        return

    # Termos proibidos (remoção automática)
    termos_proibidos = ["GABARITO", "GAB", "LIBRAS", "AMPLIADA", "SUPERAMPLIADA", "NVDA", "LEDOR", ".TXT"]

    print(f"="*70)
    print(f"LIMPEZA DE PROVAS - ENEM {ano}")
    print(f"Meta: Manter os TOP {top_n} PDFs mais relevantes por dia")
    print(f"="*70)

    amostras = obter_amostra_por_cor(ano)

    arquivos = glob.glob(os.path.join(dir_path, "*"))
    candidatos_d1 = []
    candidatos_d2 = []
    outros_arquivos = []

    # 1. Classificação dos Arquivos
    for file_path in arquivos:
        if os.path.isdir(file_path): continue
        nome_arquivo = os.path.basename(file_path)
        if nome_arquivo.startswith("."): continue
        
        # Remove automaticamente arquivos com termos proibidos
        if any(p in nome_arquivo.upper() for p in termos_proibidos):
            outros_arquivos.append(file_path)
            continue

        dia, cor, prioridade = identificar_pdf(nome_arquivo)
        
        # Busca pontuação de amostra
        score_amostra = 0
        if amostras and dia in amostras:
            score_amostra = amostras[dia].get(cor, 0)
        
        # Estrutura do candidato
        item = {
            'path': file_path,
            'name': nome_arquivo,
            'cor': cor,
            'score': score_amostra,
            'prio': prioridade
        }

        if dia == "1":
            candidatos_d1.append(item)
        elif dia == "2":
            candidatos_d2.append(item)
        else:
            outros_arquivos.append(file_path)

    # 2. Ordenação e Corte
    # Ordena por: Amostra (Decrescente) -> Prioridade (Decrescente)
    candidatos_d1.sort(key=lambda x: (x['score'], x['prio']), reverse=True)
    candidatos_d2.sort(key=lambda x: (x['score'], x['prio']), reverse=True)

    # Seleciona os Top N
    mantidos_d1 = candidatos_d1[:top_n]
    mantidos_d2 = candidatos_d2[:top_n]
    
    removidos_d1 = candidatos_d1[top_n:]
    removidos_d2 = candidatos_d2[top_n:]

    # 3. Execução (Remoção)
    count_mantidos = 0
    count_removidos = 0

    print(f"\n{'='*70}")
    print(f"DIA 1 - TOP {top_n}")
    print(f"{'='*70}")
    for item in mantidos_d1:
        print(f"✅ {item['name']}")
        print(f"   └─ Cor: {item['cor']} | Amostra: {item['score']:,} alunos | Prioridade: {item['prio']}")
        count_mantidos += 1
    
    for item in removidos_d1:
        print(f"❌ {item['name']} (score insuficiente)")
        try: 
            os.remove(item['path'])
            count_removidos += 1
        except: 
            pass

    print(f"\n{'='*70}")
    print(f"DIA 2 - TOP {top_n}")
    print(f"{'='*70}")
    for item in mantidos_d2:
        print(f"✅ {item['name']}")
        print(f"   └─ Cor: {item['cor']} | Amostra: {item['score']:,} alunos | Prioridade: {item['prio']}")
        count_mantidos += 1
    
    for item in removidos_d2:
        print(f"❌ {item['name']} (score insuficiente)")
        try: 
            os.remove(item['path'])
            count_removidos += 1
        except: 
            pass

    if outros_arquivos:
        print(f"\n{'='*70}")
        print(f"ARQUIVOS REMOVIDOS (gabaritos/especiais/não identificados)")
        print(f"{'='*70}")
        for path in outros_arquivos:
            print(f"🗑️  {os.path.basename(path)}")
            try: 
                os.remove(path)
                count_removidos += 1
            except: 
                pass

    print(f"\n{'='*70}")
    print(f"RESUMO FINAL")
    print(f"{'='*70}")
    print(f"✅ Mantidos: {count_mantidos} arquivos")
    print(f"❌ Removidos: {count_removidos} arquivos")
    print(f"{'='*70}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python _01_limpar_provas.py <ANO> <TOP>")
        print("\nExemplo: python _01_limpar_provas.py 2020 4")
        print("  └─ Mantém as 4 provas mais respondidas do Dia 1 e as 4 do Dia 2")
        sys.exit(1)

    ano_arg = sys.argv[1]
    try:
        top_arg = int(sys.argv[2])
    except ValueError:
        print("❌ Erro: TOP deve ser um número inteiro.")
        sys.exit(1)
    
    if top_arg < 1:
        print("❌ Erro: TOP deve ser maior que 0.")
        sys.exit(1)
        
    limpar_diretorio(ano_arg, top_arg)