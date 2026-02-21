'''
Filtrar apenas alunos que escolheram Inglês e gera a matriz de respostas 
a partir do RESULTADOS_ano.csv (ou MICRODADOS_ENEM_ano.csv), 
escolhendo apenas as provas TOP.

A coluna chave no CSV de resultados é a TP_LINGUA, onde:

0: Inglês

1: Espanhol

Padrão de nomenclatura de IDs de questões:
  Bloco            q_id (chave JSON)      NNN no arquivo
  ─────────────    ─────────────────      ───────────────
  Inglês  (D1)     "1" … "5"             1 … 5
  Espanhol (D1)    "01" … "05"           01 … 05
  LC (D1)          "06" … "09"           06 … 09
  LC (D1)          "10" … "50"           10 … 50
  CH (D1)          "51" … "90"           51 … 90
  CN+MT (D2)       "91" … "180"          91 … 180


**TX_RESPOSTAS_LC - 45 chars:**
as 5 primeiras posições correspondem à língua estrangeira escolhida pelo aluno.

**TX_GABARITO_LC - 50 chars:**
das 10 primeiras posições, as 5 primeiras são Inglês e as outras 5 são Espanhol.

Então para um aluno de **Inglês (TP_LINGUA=0)**:

GABARITO (50):  [IG1 IG2 IG3 IG4 IG5] [ES1 ES2 ES3 ES4 ES5] [LC06...LC50]
                 pos 0-4                pos 5-9                pos 10-49

RESPOSTA (45):  [LE1 LE2 LE3 LE4 LE5] [LC06...LC50]
                 pos 0-4 (Inglês)       pos 5-44


O casamento correto para aluno de Inglês seria:
- Resposta[0:5] → Gabarito[0:5] (Inglês)
- Resposta[5:45] → Gabarito[10:50] (LC comum)
- Gabarito[5:10] (Espanhol) é **ignorado**
'''

import pandas as pd
import sys
import os
import json
import warnings

# Silencia avisos de performance do pandas
warnings.filterwarnings("ignore")

def buscar_path_microdados(ano):
    """Garante a busca no caminho correto sem o prefixo ENEM"""
    caminho = os.path.join(ano, "DADOS", f"RESULTADOS_{ano}.csv")
    if not os.path.exists(caminho):
        caminho = os.path.join(ano, "DADOS", f"MICRODADOS_ENEM_{ano}.csv")
    return caminho if os.path.exists(caminho) else None

def carregar_mapa_provas(ano):
    path = os.path.join("ENEM", ano, "DADOS", "mapa_provas.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def carregar_id_map(ano):
    """Lê o ranking_provas para obter a área (sg_area) de cada CO_PROVA."""
    path = os.path.join("ENEM", ano, "DADOS", f"ranking_provas_{ano}.json")
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        ranking = json.load(f)
    return {item['co_prova']: item for item in ranking}

def processar_matrizes(ano, amostra_alvo):
    path_dados = buscar_path_microdados(ano)
    mapa_top   = carregar_mapa_provas(ano)

    if not path_dados:
        print(f"❌ Erro: Microdados não encontrados em {ano}/DADOS/")
        return
    if not mapa_top:
        print(f"❌ Erro: mapa_provas.json não encontrado em ENEM/{ano}/DADOS/")
        return

    # Carregar gabaritos
    path_itens = os.path.join("ENEM", ano, "DADOS", f"ITENS_PROVA_{ano}.json")
    if not os.path.exists(path_itens):
        print(f"❌ Erro: {path_itens} não encontrado.")
        return

    with open(path_itens, 'r', encoding='utf-8') as f:
        itens_data = json.load(f)

    # --- IDs das provas TOP (somente os que existem no mapa) ---
    ids_alvo = set(mapa_top.keys())

    # Verificar cobertura: todo ID do mapa deve ter gabarito no JSON
    fora_do_json = ids_alvo - set(itens_data.keys())
    if fora_do_json:
        print(f"❌ ERRO: IDs no mapa_provas sem gabarito em ITENS_PROVA: {fora_do_json}")
        print(f"   Verifique se ITENS_PROVA_{ano}.json cobre as cores do mapa_provas.json")
        return

    # Mapear pid -> (col_prova, col_resp) usando a área vinda do ranking
    id_map        = carregar_id_map(ano)
    area_para_idx = {'CN': 0, 'CH': 1, 'LC': 2, 'MT': 3}
    cols_provas   = ['CO_PROVA_CN', 'CO_PROVA_CH', 'CO_PROVA_LC', 'CO_PROVA_MT']
    cols_resps    = ['TX_RESPOSTAS_CN', 'TX_RESPOSTAS_CH', 'TX_RESPOSTAS_LC', 'TX_RESPOSTAS_MT']

    pid_para_colunas = {}
    for pid in ids_alvo:
        area = id_map.get(pid, {}).get('sg_area', '')
        idx  = area_para_idx.get(area)
        if idx is not None:
            pid_para_colunas[pid] = (cols_provas[idx], cols_resps[idx])
        else:
            print(f"⚠️  Prova {pid}: área '{area}' não reconhecida em ranking_provas_{ano}.json — pulando.")

    if not pid_para_colunas:
        print(f"❌ Erro: Nenhum pid com área reconhecida. Verifique ranking_provas_{ano}.json.")
        return

    amostras_coletadas = {pid: [] for pid in pid_para_colunas}

    print(f"🚀 Lendo: {path_dados}")
    print(f"🚀 Coletando amostra de {amostra_alvo} alunos p/ cada prova TOP (Somente Inglês)...")

    # Chunking para performance
    reader = pd.read_csv(path_dados, sep=';', encoding='latin1', chunksize=100000, low_memory=False)

    for chunk in reader:
        # FILTRO: Somente Inglês
        if 'TP_LINGUA' in chunk.columns:
            chunk = chunk[chunk['TP_LINGUA'] == 0]

        if chunk.empty:
            continue

        # Cada pid sabe exatamente qual coluna usar — sem testar as 4 áreas
        for pid, (cp, cr) in pid_para_colunas.items():
            if len(amostras_coletadas[pid]) >= amostra_alvo:
                continue

            # Robustez: converte float -> int -> str para evitar "1395.0"
            mask  = chunk[cp].fillna(-1).astype(int).astype(str) == pid
            resps = chunk.loc[mask, cr].dropna().tolist()

            vagas = amostra_alvo - len(amostras_coletadas[pid])
            amostras_coletadas[pid].extend(resps[:vagas])

        # Para se já atingiu a amostra em todas as provas
        if all(len(amostras_coletadas[pid]) >= amostra_alvo for pid in pid_para_colunas):
            break

    # --- GERAÇÃO DAS MATRIZES BINÁRIAS ---
    dir_matriz = os.path.join("ENEM", ano, "DADOS", "MATRIZ")
    os.makedirs(dir_matriz, exist_ok=True)

    for pid, resps in amostras_coletadas.items():
        if not resps:
            print(f"⚠️  Prova {pid}: Nenhuma resposta coletada.")
            continue

        prova_info = itens_data[pid]  # garantido existir pela verificação anterior
        questions  = prova_info['QUESTIONS']

        # LÓGICA DO GABARITO:
        # Como filtramos por Inglês, ignoramos as chaves de Espanhol ("01" a "05")
        # para que o tamanho do gabarito (45) bata com a string TX_RESPOSTAS_LC (45)
        chaves_validas = [k for k in questions.keys() if k not in ["01", "02", "03", "04", "05"]]
        chaves_ord     = sorted(chaves_validas, key=lambda x: int(x))

        gabarito = "".join([questions[k]['answer'] for k in chaves_ord])

        # Compara resposta do aluno com gabarito (Matriz de Acertos)
        matriz_bin = []
        for r in resps:
            if len(r) == len(gabarito):
                linha = [1 if a == b else 0 for a, b in zip(r, gabarito)]
                matriz_bin.append(linha)

        if matriz_bin:
            amostra_str = str(amostra_alvo).zfill(6)
            nome_arq    = f"{pid}_{amostra_str}_data.csv"
            pd.DataFrame(matriz_bin).to_csv(
                os.path.join(dir_matriz, nome_arq), index=False, header=False
            )
            print(f"✅ Matriz salva: {nome_arq} ({len(matriz_bin)} alunos)")
        else:
            print(f"⚠️  Prova {pid}: Nenhuma resposta com tamanho compatível com o gabarito ({len(gabarito)}).")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python _03_enem2matriz.py <ANO> <AMOSTRA>")
    else:
        processar_matrizes(sys.argv[1], int(sys.argv[2]))