#!/bin/bash
# ==============================================================================
# SCRIPT: _06_processar_enem.sh (CORRIGIDO PARA ESPAÇOS E MÚLTIPLOS IDs)
# ==============================================================================

INPUT_PDF="$1"
OUTPUT_DIR="$2"
ANO="$3"
NOME_PROVA_TEXTO="$4" # ex: ENEM_2024_P1_CAD_04_DIA_1_VERDE

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }


if [ -z "$NOME_PROVA_TEXTO" ]; then
    echo "❌ Erro: Argumentos insuficientes."
    exit 1
fi

# 1. Identifica TODOS os CO_PROVA numéricos vinculados a este PDF via ranking [cite: 13, 16]
CO_PROVAS=$(python3 -c "import json, sys; \
    r = json.load(open('ENEM/$ANO/DADOS/ranking_provas_$ANO.json')); \
    ids = [str(x['co_prova']) for x in r if x['arquivo_pdf'] == '$NOME_PROVA_TEXTO.pdf']; \
    print(' '.join(ids))")

echo "   [FATIAMENTO] PDF: $NOME_PROVA_TEXTO | IDs Detectados: $CO_PROVAS"

# 2. Executa fatiamento comum do PDF (Uma única vez)
TEMP_FATIAS="_temp_${ANO}_$(date +%s)"
mkdir -p "$TEMP_FATIAS"
python3 analisar_e_fatiar.py "$INPUT_PDF" "$TEMP_FATIAS"
STATUS=$?

if [ $STATUS -ne 0 ]; then
    echo "❌ Erro no script de fatiamento."
    rm -rf "$TEMP_FATIAS"
    exit 1
fi

# 3. Converte PDFs para PNG (Aspas duplas protegem nomes com espaços) 
mkdir -p "$OUTPUT_DIR"
for pdf_slice in "$TEMP_FATIAS"/*.pdf; do
    [ -e "$pdf_slice" ] || continue
    name=$(basename "$pdf_slice" .pdf)
    pdftoppm -png -r 150 -cropbox -singlefile "$pdf_slice" "$OUTPUT_DIR/$name" 
done
rm -rf "$TEMP_FATIAS"

# 4. Itera sobre cada CO_PROVA para gerar as imagens data individuais [cite: 13, 16]
for CID in $CO_PROVAS; do
    log_info "      → Gerando imagens para ID: $CID"
    log_info "Comando: \npython3 _06b_gerar_img_data.py \"$ANO\" \"$CID\" \"$NOME_PROVA_TEXTO\""

    python3 _06b_gerar_img_data.py "$ANO" "$CID" "$NOME_PROVA_TEXTO"
done
