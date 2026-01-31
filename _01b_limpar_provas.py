import os
import sys
import json
import glob
import shutil

def limpar_provas(ano, top_n):
    top_n = int(top_n)
    
    # 1. Caminho do ranking gerado pelo script anterior
    ranking_path = os.path.join("ENEM", ano, "DADOS", f"ranking_provas_{ano}.json")
    
    if not os.path.exists(ranking_path):
        print(f"❌ Erro: Ranking não encontrado em {ranking_path}")
        return

    with open(ranking_path, 'r', encoding='utf-8') as f:
        ranking = json.load(f)

    # 2. Identificar quais arquivos PDF devem ser mantidos
    # O critério agora é: os PDFs que aparecem nos TOP N grupos de cada dia/aplicação
    # Agrupamos por dia para respeitar o limite de top_n por dia
    arquivos_para_manter = set()
    
    for dia in ["1", "2"]:
        # Filtra cadernos do dia e remove duplicatas de PDF (pois LC/CH ou CN/MT compartilham o mesmo PDF)
        cadernos_dia = [item for item in ranking if item['dia'] == dia]
        
        # Como o ranking já vem ordenado por total_alunos, pegamos os PDFs únicos dos primeiros registros
        vistos = set()
        pdfs_do_dia = []
        for c in cadernos_dia:
            if c['arquivo_pdf'] not in vistos and c['arquivo_pdf'] != "NÃO ENCONTRADO":
                pdfs_do_dia.append(c['arquivo_pdf'])
                vistos.add(c['arquivo_pdf'])
        
        # Mantém apenas os TOP N arquivos PDF reais de cada dia
        arquivos_para_manter.update(pdfs_do_dia[:top_n])

    # 3. Mapear todos os PDFs existentes na pasta
    diretorio_pdfs = os.path.join(ano, "PROVAS E GABARITOS")
    todos_arquivos_no_disco = glob.glob(os.path.join(diretorio_pdfs, "*.pdf"))

    print(f"--- 🧹 Limpeza Baseada em Ranking ENEM {ano} ---")
    print(f"Mantendo os {top_n} cadernos mais voados de cada dia.")

    count_del = 0
    mantidos = []

    # 4. Execução da Limpeza
    for path in todos_arquivos_no_disco:
        nome_arquivo = os.path.basename(path)
        
        if nome_arquivo in arquivos_para_manter:
            mantidos.append(nome_arquivo)
            continue
        else:
            # Se não está na lista de "manter", tchau.
            try:
                os.remove(path)
                # Remove também a pasta de imagens (fatias) se existir
                pasta_fatias = path.replace(".pdf", "")
                if os.path.exists(pasta_fatias):
                    shutil.rmtree(pasta_fatias)
                count_del += 1
            except Exception as e:
                print(f"      [ERRO] ao deletar {nome_arquivo}: {e}")

    print(f"\n✅ MANTIDOS ({len(mantidos)}):")
    for m in sorted(mantidos):
        print(f"   [OK] {m}")

    print(f"\n🗑️  TOTAL REMOVIDO: {count_del} arquivos e suas respectivas pastas de fatias.")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        limpar_provas(sys.argv[1], sys.argv[2])
    else:
        print("Uso: python _01b_limpar_provas.py <ano> <top_n>")