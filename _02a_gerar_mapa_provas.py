import os
import json
import sys

def gerar_mapa_provas(ano, top_n):
    top_n = int(top_n)
    
    # 1. Caminhos de arquivos
    path_ranking = os.path.join("ENEM", ano, "DADOS", f"ranking_provas_{ano}.json")
    arquivo_json_saida = os.path.join("ENEM", ano, "DADOS", "mapa_provas.json")

    if not os.path.exists(path_ranking):
        print(f"❌ Erro: Ranking não encontrado em {path_ranking}")
        return

    with open(path_ranking, 'r', encoding='utf-8') as f:
        ranking_completo = json.load(f)

    # 2. Identificar os arquivos PDF que estão no TOP N de cada dia
    pdfs_permitidos = set()
    for dia in ["1", "2"]:
        cadernos_dia = [item for item in ranking_completo if item['dia'] == dia]
        
        vistos = set()
        pdfs_unicos = []
        for c in cadernos_dia:
            if c['arquivo_pdf'] not in vistos and c['arquivo_pdf'] != "NÃO ENCONTRADO":
                pdfs_unicos.append(c['arquivo_pdf'])
                vistos.add(c['arquivo_pdf'])
        
        # Adiciona apenas os TOP N arquivos PDF físicos ao set de permitidos
        pdfs_permitidos.update(pdfs_unicos[:top_n])

    # 3. Agrupar CO_PROVA por PDF (Mapeamento)
    # Ex: O PDF "AZUL_DIA_1" tem CO_PROVA 511 (LC) e 507 (CH). O mapa será {511: "507_511", 507: "507_511"}
    mapa_agrupado = {}
    for pdf in pdfs_permitidos:
        # Encontra todos os itens no ranking que usam este PDF específico
        itens_deste_pdf = [r for r in ranking_completo if r['arquivo_pdf'] == pdf]
        
        codigos = sorted([str(item['co_prova']) for item in itens_deste_pdf])
        
        if len(codigos) >= 2:
            identificador_grupo = "_".join(codigos)
            for cod in codigos:
                mapa_agrupado[cod] = identificador_grupo
            print(f"✅ Mapeado: PDF '{pdf}' -> IDs {codigos}")

    # 4. Salvar o mapa final
    os.makedirs(os.path.dirname(arquivo_json_saida), exist_ok=True)
    with open(arquivo_json_saida, 'w', encoding='utf-8') as f:
        json.dump(mapa_agrupado, f, indent=4, ensure_ascii=False)

    print(f"\n✨ Mapa de provas gerado com sucesso: {len(mapa_agrupado)} IDs mapeados.")
    print(f"Caminho: {arquivo_json_saida}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        gerar_mapa_provas(sys.argv[1], sys.argv[2])
    else:
        print("Uso: python _02a_gerar_mapa_provas.py <ano> <top_n>")