import re
import os
import json
import sys
import glob

def limpar_label(label):
    """Normaliza o nome da cor/tipo"""
    label = label.replace("'", "").replace('"', "").strip().upper()
    
    substituicoes = {
        'Ã': 'A', 'Â': 'A', 'Ç': 'C', 'Ê': 'E', 'É': 'E',
        ' - ': '_', ' ': '_', '(': '', ')': ''
    }
    for orig, dest in substituicoes.items():
        label = label.replace(orig, dest)
    return label

def extrair_vetor_r(conteudo, nome_coluna):
    """
    Busca no texto do R a definição de levels e labels.
    Aceita diversos formatos e espaçamentos.
    """
    padroes = [
        rf"[\w\.]+\${re.escape(nome_coluna)}\s*<-\s*factor\s*\([\w\.]+\${re.escape(nome_coluna)}\s*,\s*levels\s*=\s*c\s*\((.*?)\)\s*,\s*labels\s*=\s*c\s*\((.*?)\)\)",
        rf"{re.escape(nome_coluna)}\s*<-\s*factor\s*\([^,]+,\s*levels\s*=\s*c\s*\((.*?)\)\s*,\s*labels\s*=\s*c\s*\((.*?)\)\)",
        rf"factor\s*\([^,]*{re.escape(nome_coluna)}[^,]*,\s*levels\s*=\s*c\s*\((.*?)\)\s*,\s*labels\s*=\s*c\s*\((.*?)\)\)"
    ]
    
    for padrao in padroes:
        match = re.search(padrao, conteudo, re.DOTALL | re.IGNORECASE)
        if match:
            try:
                levels_raw = match.group(1).replace('\n', '').replace(' ', '')
                labels_raw = match.group(2).replace('\n', '')

                levels = [l.strip() for l in levels_raw.split(',')]
                labels = [limpar_label(l.strip().strip("'").strip('"')) for l in labels_raw.split(',')]

                if len(levels) == len(labels) and len(levels) > 0:
                    return dict(zip(labels, levels))
            except:
                continue

    return {}

def gerar_mapa(ano):
    dir_inputs = f'./{ano}/INPUTS'
    dir_saida = f'ENEM/{ano}/DADOS'
    padrao_busca = os.path.join(dir_inputs, '*.R')

    arquivos_encontrados = glob.glob(padrao_busca)
    if not arquivos_encontrados:
        print(f"⚠️  Nenhum arquivo R encontrado em {dir_inputs}")
        return

    os.makedirs(dir_saida, exist_ok=True)
    arquivo_json_saida = os.path.join(dir_saida, "mapa_provas.json")

    mapa_cn, mapa_ch, mapa_lc, mapa_mt = {}, {}, {}, {}
    arquivo_sucesso = None

    # -------------------------------------------------------------
    # 1. Ler arquivos R para extrair os vetores de provas
    # -------------------------------------------------------------
    for arquivo_r in arquivos_encontrados:
        print(f"🔍 Tentando arquivo: {os.path.basename(arquivo_r)}")

        try:
            try:
                with open(arquivo_r, 'r', encoding='utf-8') as f:
                    conteudo_bruto = f.read()
            except UnicodeDecodeError:
                with open(arquivo_r, 'r', encoding='latin1') as f:
                    conteudo_bruto = f.read()

            # remover comentarios iniciais
            linhas = []
            for line in conteudo_bruto.split("\n"):
                if line.lstrip().startswith("#"):
                    linhas.append(line.replace("#", " ", 1))
                else:
                    linhas.append(line)

            conteudo = "\n".join(linhas)

        except Exception as e:
            print(f"   ⚠️ Erro ao ler arquivo: {e}")
            continue

        mapa_cn = extrair_vetor_r(conteudo, "CO_PROVA_CN")
        mapa_ch = extrair_vetor_r(conteudo, "CO_PROVA_CH")
        mapa_lc = extrair_vetor_r(conteudo, "CO_PROVA_LC")
        mapa_mt = extrair_vetor_r(conteudo, "CO_PROVA_MT")

        if any([mapa_cn, mapa_ch, mapa_lc, mapa_mt]):
            arquivo_sucesso = arquivo_r
            print("   ✅ Vetores encontrados!")
            break
        else:
            print("   ⚠️ Vetores não encontrados neste arquivo.")

    if not any([mapa_cn, mapa_ch, mapa_lc, mapa_mt]):
        print("\n❌ Nenhum vetor encontrado em nenhum arquivo R.")
        return

    print(f"\n📄 Extraído de: {os.path.basename(arquivo_sucesso)}\n")

    # -------------------------------------------------------------
    # 2. Ler PDFs e extrair combinações DIA + COR
    # -------------------------------------------------------------
    dir_pdfs = f'./{ano}/PROVAS E GABARITOS'
    pdfs = glob.glob(os.path.join(dir_pdfs, "*.pdf"))

    combos_disponiveis = set()

    for pdf in pdfs:
        nome = os.path.basename(pdf).upper()

        achado = re.search(r"DIA_[12]_[A-ZÇÃ]+", nome)
        if achado:
            combos_disponiveis.add(achado.group(0))

    print("📌 Combinações disponíveis nos PDFs:", combos_disponiveis, "\n")

    # -------------------------------------------------------------
    # 3. Gerar mapa final APENAS para provas realmente existentes
    # -------------------------------------------------------------
    mapa_final = {}

    # -------------------- DIA 1 (LC + CH) -------------------------
    for cor, codigo_lc in mapa_lc.items():
        if cor in mapa_ch:
            codigo_ch = mapa_ch[cor]
            combo_pdf = f"DIA_1_{cor}"

            if combo_pdf in combos_disponiveis:
                valor = f"{codigo_lc}_{codigo_ch}"
                mapa_final[codigo_lc] = valor
                mapa_final[codigo_ch] = valor
                print(f"[DIA 1 OK] {cor}: {valor}")
            else:
                print(f"[IGNORADO DIA 1] {cor}: sem PDF → {combo_pdf}")

    print()

    # -------------------- DIA 2 (CN + MT) -------------------------
    for cor, codigo_cn in mapa_cn.items():
        if cor in mapa_mt:
            codigo_mt = mapa_mt[cor]
            combo_pdf = f"DIA_2_{cor}"

            if combo_pdf in combos_disponiveis:
                valor = f"{codigo_cn}_{codigo_mt}"
                mapa_final[codigo_cn] = valor
                mapa_final[codigo_mt] = valor
                print(f"[DIA 2 OK] {cor}: {valor}")
            else:
                print(f"[IGNORADO DIA 2] {cor}: sem PDF → {combo_pdf}")

    # -------------------------------------------------------------
    # 4. Salvar JSON
    # -------------------------------------------------------------
    with open(arquivo_json_saida, "w", encoding="utf-8") as f:
        json.dump(mapa_final, f, indent=4)

    print(f"\n✅ Mapa final salvo em: {arquivo_json_saida}")
    print(f"   Total de IDs mapeados: {len(mapa_final)}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <ANO>")
        sys.exit(1)

    gerar_mapa(sys.argv[1])
