import os
import json
import pandas as pd
import sys
import glob
from sklearn.cluster import KMeans
import numpy as np

def carregar_itens_mapeamento(ano):
    """Lê o CSV de itens para traduzir o ID da prova em Cor, Dia, Área e Posição."""
    caminho_csv = os.path.join(ano, "DADOS", f"ITENS_PROVA_{ano}.csv")
    
    if os.path.exists(caminho_csv):
        df_itens = pd.read_csv(caminho_csv, sep=';', encoding='latin1')
        
        # Agrupa por CO_PROVA para obter metadados do bloco de questões
        summary = df_itens.groupby('CO_PROVA').agg(
            TX_COR=('TX_COR', 'first'),
            SG_AREA=('SG_AREA', 'first'),
            POS_MIN=('CO_POSICAO', 'min'),
            POS_MAX=('CO_POSICAO', 'max')
        ).reset_index()
        
        mapeamento = {}
        for _, row in summary.iterrows():
            cod = str(int(row['CO_PROVA']))
            cor_orig = str(row['TX_COR']).upper()
            
            # Normalização para match com nome de arquivo físico
            cor_norm = cor_orig
            if cor_norm == "BRANCA": cor_norm = "BRANCO"
            if cor_norm == "AMARELA": cor_norm = "AMARELO"
            
            area = str(row['SG_AREA']).upper()
            dia = "1" if any(x in area for x in ['LC', 'CH']) else "2"
            
            mapeamento[cod] = {
                "tx_cor": cor_orig,
                "cor_busca": cor_norm,
                "dia": dia,
                "sg_area": area,
                "co_posicao": f"{int(row['POS_MIN'])}-{int(row['POS_MAX'])}"
            }
        return mapeamento
    return None

def listar_pdfs_disponiveis(ano):
    """Mapeia os arquivos físicos reais no diretório."""
    diretorio = os.path.join(ano, "PROVAS E GABARITOS")
    arquivos = glob.glob(os.path.join(diretorio, "*.pdf"))
    lista_pdfs = []
    
    for path in arquivos:
        nome_original = os.path.basename(path)
        nome_upper = nome_original.upper()
        
        # Filtros de exclusão (Gabaritos e Adaptadas)
        if any(x in nome_upper for x in ["GAB", "DIGITAL", "AMPLIADA", "SUPERAMPLIADA", "LIBRAS", "LEDOR"]):
            continue
            
        dia = "1" if "DIA_1" in nome_upper else "2"
        app = "P2" if "P2" in nome_upper else "P1"
        
        cor_encontrada = ""
        for c in ["AZUL", "AMARELO", "BRANCO", "ROSA", "CINZA", "VERDE", "LARANJA"]:
            if c in nome_upper:
                cor_encontrada = c
                break
            
        lista_pdfs.append({
            "arquivo_real": nome_original,
            "dia": dia,
            "cor": cor_encontrada,
            "app": app
        })
    return lista_pdfs

def gerar_json_ranking(ano):
    # 1. Definição de caminhos e busca flexível do arquivo
    dados_dir = os.path.join(ano, "DADOS")
    
    # Lista de nomes possíveis para os microdados (Padrão Antigo e Novo)
    nomes_possiveis = [
        f"MICRODADOS_ENEM_{ano}.csv",
        f"RESULTADOS_{ano}.csv"
    ]
    
    path_microdados = None
    for nome in nomes_possiveis:
        tentativa = os.path.join(dados_dir, nome)
        if os.path.exists(tentativa):
            path_microdados = tentativa
            print(f"📖 Microdados encontrados: {path_microdados}")
            break

    if not path_microdados:
        print(f"❌ Erro: Nenhum arquivo de microdados encontrado em {dados_dir}.")
        print(f"   Procurados: {', '.join(nomes_possiveis)}")
        return

    # Carrega metadados e lista arquivos físicos
    id_map = carregar_itens_mapeamento(ano) or {}
    pdfs_fisicos = listar_pdfs_disponiveis(ano)

    print(f"⏳ Processando microdados de {ano}...")
    cols = ['CO_PROVA_CN', 'CO_PROVA_CH', 'CO_PROVA_LC', 'CO_PROVA_MT']
    
    # Leitura dos microdados usando o path_microdados definido acima
    # Adicionado low_memory=False para evitar warnings em arquivos grandes
    df = pd.read_csv(path_microdados, sep=';', encoding='latin1', usecols=cols, low_memory=False)
    
    counts_dict = {}
    for col in cols:
        counts = df[col].dropna().value_counts().to_dict()
        for pid, qtd in counts.items():
            pid_str = str(int(pid))
            counts_dict[pid_str] = counts_dict.get(pid_str, 0) + qtd

    # 1. Preparar dados para o Ranking e Clusterização
    ranking_raw = []
    volumes = []
    for pid, total in counts_dict.items():
        if total <= 1000: continue
        meta = id_map.get(pid, {"tx_cor": "NI", "cor_busca": "NI", "dia": "?", "sg_area": "NI", "co_posicao": "NI"})        
        
        item = {
            "co_prova": pid, 
            "tx_cor": meta["tx_cor"],
            "sg_area": meta["sg_area"],
            "co_posicao": meta["co_posicao"],
            "dia": meta["dia"], 
            "total_alunos": int(total),
            "_cor_busca": meta["cor_busca"] # Usado apenas para o match do PDF
        }
        ranking_raw.append(item)
        volumes.append(total)

    if not ranking_raw:
        print("⚠️ Nenhum dado encontrado.")
        return

    # 2. LÓGICA DE CLUSTERIZAÇÃO (K-Means)
    X = np.array(volumes).reshape(-1, 1)
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10).fit(X)
    idx_p1 = np.argmax(kmeans.cluster_centers_)
    
    for i, item in enumerate(ranking_raw):
        label = kmeans.labels_[i]
        item["aplicacao"] = "P1" if label == idx_p1 else "P2"
    
    # 3. ASSOCIAÇÃO DO NOME EXATO DO PDF E LIMPEZA
    lista_final = []
    for item in ranking_raw:
        # Busca o arquivo físico correspondente
        item["arquivo_pdf"] = "NÃO ENCONTRADO"
        for pdf in pdfs_fisicos:
            # Compara Cor normalizada, Dia e Tipo de Aplicação (P1/P2)
            if (pdf['cor'] == item['_cor_busca'] and 
                pdf['dia'] == item['dia'] and 
                pdf['app'] == item['aplicacao']):
                item["arquivo_pdf"] = pdf['arquivo_real']
                break
        
        # Remove campo auxiliar e adiciona à lista final
        temp_item = item.copy()
        temp_item.pop("_cor_busca", None)
        lista_final.append(temp_item)

    # Ordenar por volume de alunos
    lista_final.sort(key=lambda x: x['total_alunos'], reverse=True)

    # 4. SALVAMENTO
    output_path = os.path.join("ENEM", ano, "DADOS", f"ranking_provas_{ano}.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(lista_final, f, indent=4, ensure_ascii=False)

    print(f"✅ Sucesso! JSON salvo em: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        gerar_json_ranking(sys.argv[1])