import json
import sys
import pandas as pd
import os

# Configurações globais
qstr = '{"answer": "__answer__", "ability": __ability__, "id": __id__, "percentage": 0, "irt": [], "images": [], "videos": [], "subareas": [] }'

def carregar_mapa_provas(ano):
    """Carrega o JSON de mapeamento de provas gerado pelo _00_gerar_mapa_provas.py"""
    caminho_mapa = f'ENEM/{ano}/DADOS/mapa_provas.json'
    if os.path.exists(caminho_mapa):
        try:
            with open(caminho_mapa, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler mapa de provas: {e}")
    else:
        print(f"⚠️  Aviso: Mapa de provas não encontrado em {caminho_mapa}. Usando IDs originais.")
    return {}

def getGabs(gab, mapa_tipos_prova, ranking_dados):
    try:
        # Tenta ler com encoding latin1 (comum em arquivos do governo)
        df = pd.read_csv(gab, sep=';', index_col=0, encoding='latin1')
    except UnicodeDecodeError:
        df = pd.read_csv(gab, sep=';', index_col=0, encoding='cp1252')
    except Exception as e:
        print(f"Erro ao abrir CSV: {e}")
        return {}

    gab_dict = {}
    unique_provas = sorted(df['CO_PROVA'].unique())

    for v in unique_provas:
        str_v = str(v)
        dfAux = df.loc[df['CO_PROVA'] == v]

        d = {}
        if dfAux.empty: continue
            
        area50 = len(list(dfAux['TX_GABARITO']))
        habilidade = list(dfAux['CO_HABILIDADE'])
        codQuestion = list(dfAux['CO_ITEM'])
        
        # Tratamento seguro para Cor e Área
        try:
            val_cor = list(dfAux['TX_COR'])[0]
            COR = "DESCONHECIDA" if pd.isna(val_cor) else str(val_cor).upper()
        except: COR = "DESCONHECIDA"

        if COR == 'BRANCA': COR = 'BRANCO'
        if COR == 'AMARELA': COR = 'AMARELO'
        
        try:
            val_area = list(dfAux['SG_AREA'])[0]
            AREA = "ND" if pd.isna(val_area) else str(val_area)
        except: AREA = "ND"

        # --- APLICA O MAPEAMENTO ---
        str_v = str(v)
        # Se encontrar no mapa, usa o composto (ex: 511_507), senão usa o original
        proof_type = mapa_tipos_prova.get(str_v, str_v)

        for qi, answer in enumerate(list(dfAux['TX_GABARITO'])):
            hab_val = str(int(habilidade[qi])) if pd.notna(habilidade[qi]) else "null"
            item_json_str = qstr.replace('__answer__', str(answer)) \
                                .replace('__ability__', hab_val) \
                                .replace('__id__', str(codQuestion[qi]))
            aux = json.loads(item_json_str)
            
            if area50 == 50: 
                if qi < 5: d[str(qi + 1)] = aux
                else: d[str(qi - 4).zfill(2)] = aux
            else:
                d[str(qi + 1).zfill(2)] = aux

        # gab_dict[str(v)] = {'COR': COR, "AREA": AREA, "PROOF_TYPE": proof_type, "QUESTIONS": d}
        
        # 1. Obter informações extras do dicionário ranking_dados
        # (Certifique-se de que ranking_dados foi carregado como um dicionário de co_prova)
        info_extra = ranking_dados.get(str_v, {})

        # 2. Atualizar o dicionário final com os novos campos solicitados
        gab_dict[str(v)] = {
            'COR': COR, 
            "AREA": AREA, 
            "PROOF_TYPE": proof_type, 
            "DIA": info_extra.get('dia', "ND"),                 # Novo
            "CO_POSICAO": info_extra.get('co_posicao', "ND"),   # Novo
            "TOTAL_ALUNOS": info_extra.get('total_alunos', 0),  # Novo
            "APLICACAO": info_extra.get('aplicacao', "ND"),     # Novo
            "ARQUIVO_PDF": info_extra.get('arquivo_pdf', ""),   # Novo
            "QUESTIONS": d
        }

    return gab_dict

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <ANO>")
        sys.exit(1)

    # Aceita múltiplos anos se necessário
    names = [str(i) for i in range(2009, 2030)]

    for arg in sys.argv[1:]:
        if arg in names:
            ano = arg
            
            path_base = f'./{ano}/DADOS/'
            gab_file = os.path.join(path_base, f'ITENS_PROVA_{ano}.csv')

            # 1. Carrega o mapa e o ranking
            mapa_atual = carregar_mapa_provas(ano)
            
            # ADICIONAR ESTA LINHA:
            path_ranking = f'ENEM/{ano}/DADOS/ranking_provas_{ano}.json'
            ranking_dados = {}
            if os.path.exists(path_ranking):
                with open(path_ranking, 'r', encoding='utf-8') as f:
                    # Cria um dicionário indexado pelo co_prova para busca rápida
                    ranking_dados = {str(item['co_prova']): item for item in json.load(f)}
            
            # ALTERAR A CHAMADA:
            if os.path.exists(gab_file):
                gabsDict = getGabs(gab_file, mapa_atual, ranking_dados)

            # # 1. Carrega o mapa específico do ano
            # mapa_atual = carregar_mapa_provas(ano)
            
            # path_base = f'./{ano}/DADOS/'
            # gab_file = os.path.join(path_base, f'ITENS_PROVA_{ano}.csv')
            
            # print(f'Processando gabarito: {gab_file}')
            
            # if os.path.exists(gab_file):
            #     gabsDict = getGabs(gab_file, mapa_atual)
                
                # Salva no destino correto (ENEM/ANO/DADOS) ou no local (ANO/DADOS)
                # O script original salvava no mesmo local do CSV.
                # Se quiser salvar em ENEM/ANO/DADOS, altere aqui.
                # Vou manter a lógica original de salvar ao lado do CSV, mas sugiro mover.
                
                # Opção A: Salvar ao lado do CSV
                output_file = gab_file.replace('.csv', '.json')
                
                # Opção B (Melhor): Salvar na pasta estruturada ENEM
                output_folder_final = f"ENEM/{ano}/DADOS"
                if not os.path.exists(output_folder_final):
                    os.makedirs(output_folder_final)
                output_file_final = os.path.join(output_folder_final, f'ITENS_PROVA_{ano}.json')

                print(f'Salvando JSON: {output_file_final}')
                
                with open(output_file_final, 'w', encoding='utf-8') as f:
                    json.dump(gabsDict, f, indent=4, sort_keys=False, ensure_ascii=False)
                
                # Cópia para compatibilidade legada se necessário
                # with open(output_file, 'w', encoding='utf-8') as f:
                #    json.dump(gabsDict, f, indent=4, sort_keys=False, ensure_ascii=False)

            else:
                print(f"Arquivo CSV não encontrado: {gab_file}")