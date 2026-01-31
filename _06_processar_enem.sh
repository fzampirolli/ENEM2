#!/bin/bash
# ==============================================================================
# SCRIPT: _04_processar_enem.sh
# DESCRIÇÃO: Fatia PDF, salva fatias em PDF (backup) e converte para PNG.
# USO: ./_04_processar_enem.sh <CAMINHO_PDF> <DIR_SAIDA_IMAGENS>
# ==============================================================================

INPUT_PDF="$1"
OUTPUT_DIR="$2"

# --- ADICIONE/MOVA ESTAS LINHAS PARA CÁ ---
DIR_IMAGENS_ROOT=$(dirname "$OUTPUT_DIR")      # .../imagens
DIR_RAIZ_PROVAS=$(dirname "$DIR_IMAGENS_ROOT")  # .../PROVAS_E_GABARITOS
NOME_PROVA=$(basename "$OUTPUT_DIR")
PDFS_DIR="${DIR_RAIZ_PROVAS}/pdfs/${NOME_PROVA}"
# ------------------------------------------

if [ -z "$INPUT_PDF" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "❌ Erro: Argumentos faltando em _04_processar_enem.sh"
    exit 1
fi

# ==================== VERIFICAÇÃO DE EXISTÊNCIA ====================
# Agora $PDFS_DIR e $OUTPUT_DIR possuem valores reais
if [ -d "$PDFS_DIR" ] && [ "$(ls -A "$PDFS_DIR"/*.pdf 2>/dev/null)" ] && \
   [ -d "$OUTPUT_DIR" ] && [ "$(ls -A "$OUTPUT_DIR"/*.png 2>/dev/null)" ]; then
    echo "   [PULAR] A prova '$NOME_PROVA' já possui fatias PDF e imagens PNG. Ignorando..."
    exit 0
fi
# ===================================================================

echo "   [FATIAMENTO] Iniciando processamento de nova prova..."

echo "      PDF: $(basename "$INPUT_PDF")"

# Define diretório de backup para os PDFs (ao lado da pasta imagens)
# Se OUTPUT_DIR for .../imagens/PROVA_X, PDFS_DIR será .../pdfs/PROVA_X
DIR_IMAGENS_ROOT=$(dirname "$OUTPUT_DIR")     # .../imagens
DIR_RAIZ_PROVAS=$(dirname "$DIR_IMAGENS_ROOT") # .../PROVAS_E_GABARITOS
NOME_PROVA=$(basename "$OUTPUT_DIR")
PDFS_DIR="${DIR_RAIZ_PROVAS}/pdfs/${NOME_PROVA}"

echo "      Imgs: .../imagens/$NOME_PROVA"
echo "      Pdfs: .../pdfs/$NOME_PROVA"

# 1. Configuração do Ambiente Python
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    source .venv/bin/activate
    pip install pdfplumber pymupdf -q
else
    source .venv/bin/activate
fi

# 2. Prepara diretórios
# Limpa imagens antigas
if [ -d "$OUTPUT_DIR" ]; then rm -f "$OUTPUT_DIR"/*.png; else mkdir -p "$OUTPUT_DIR"; fi
# Limpa PDFs antigos
if [ -d "$PDFS_DIR" ]; then rm -f "$PDFS_DIR"/*.pdf; else mkdir -p "$PDFS_DIR"; fi

# Diretório temporário
TEMP_FATIAS="_temp_fatias_$(date +%s)"
mkdir -p "$TEMP_FATIAS"

# 3. Executa o Script Python de Fatiamento
python3 analisar_e_fatiar.py "$INPUT_PDF" "$TEMP_FATIAS"
STATUS=$?

if [ $STATUS -ne 0 ]; then
    echo "❌ Erro no script Python de fatiamento."
    rm -rf "$TEMP_FATIAS"
    deactivate
    exit 1
fi

deactivate

# 4. SALVA OS PDFS (Cópia de segurança solicitada)
echo "   [BACKUP] Salvando fatias em PDF..."
cp "$TEMP_FATIAS"/*.pdf "$PDFS_DIR/"

# 5. Converte PDFs fatiados para PNG
if ! command -v pdftoppm &> /dev/null; then
    echo "❌ Erro: 'pdftoppm' não instalado. Instale poppler-utils."
    exit 1
fi

echo "   [CONVERSÃO] Gerando PNGs..."
COUNT=0
for pdf_slice in "$TEMP_FATIAS"/*.pdf; do
    [ -e "$pdf_slice" ] || continue
    name=$(basename "$pdf_slice" .pdf)
    
    # 150 DPI para equilíbrio entre qualidade e tamanho
    pdftoppm -png -r 150 -cropbox -singlefile "$pdf_slice" "$OUTPUT_DIR/$name"
    ((COUNT++))
done

# 6. Limpeza do temporário (mas os PDFs já estão salvos em $PDFS_DIR)
rm -rf "$TEMP_FATIAS"

echo "   ✅ Sucesso: $COUNT questões processadas."