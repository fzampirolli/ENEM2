#!/bin/bash

# =====================================================================
# Pipeline Automatizado ENEM - Versão 2.0
# =====================================================================
# Uso: ./_00_all.sh <ANO> [AMOSTRA] [TOP]
#
# Argumentos:
#   ANO      - Ano do ENEM (obrigatório)
#   AMOSTRA  - Tamanho da amostra (padrão: 2000)
#   TOP      - Nº de PDFs por dia (padrão: 2)
#
# Exemplos:
#   ./_00_all.sh 2020              # Usa padrões (2000, 2)
#   ./_00_all.sh 2020 5000         # Amostra 5000, TOP 2
#   ./_00_all.sh 2020 5000 4       # Amostra 5000, TOP 4
# 
# Instalações necessárias:
#   python3 -m venv .venv
#   source .venv/bin/activate
#   pip install -r requirements.txt
## pip freeze > requirements.txt
# =====================================================================

set -e  # Interrompe se algum comando falhar

# ==================== CONFIGURAÇÃO ====================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função de log
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# ==================== VALIDAÇÃO DE ARGUMENTOS ====================

if [ -z "$1" ]; then
    echo "❌ Uso: $0 <ANO> [AMOSTRA] [TOP]"
    echo ""
    echo "Exemplos:"
    echo "  $0 2020              # Usa padrões (amostra=2000, top=2)"
    echo "  $0 2020 5000         # Amostra 5000, top=2"
    echo "  $0 2020 5000 4       # Amostra 5000, top=4"
    echo ""
    echo "Para verificar anos disponíveis:"
    echo "  python3 _00_enem_config.py --check-all"
    exit 1
fi

ANO="$1"
AMOSTRA="${2:-2000}"  # Padrão: 2000
TOP="${3:-2}"         # Padrão: 2

# Valida se ANO é número
if ! [[ "$ANO" =~ ^[0-9]{4}$ ]]; then
    log_error "ANO deve ser um número de 4 dígitos (ex: 2020)"
fi

# Valida se AMOSTRA é número
if ! [[ "$AMOSTRA" =~ ^[0-9]+$ ]]; then
    log_error "AMOSTRA deve ser um número inteiro positivo"
fi

# Valida se TOP é número
if ! [[ "$TOP" =~ ^[0-9]+$ ]]; then
    log_error "TOP deve ser um número inteiro positivo"
fi

# ==================== VERIFICAÇÃO PRÉVIA ====================

echo ""
echo "======================================================================"
echo "🚀 PIPELINE ENEM $ANO - Versão Automatizada"
echo "======================================================================"
echo "📊 Configurações:"
echo "   • Ano: $ANO"
echo "   • Amostra: $AMOSTRA participantes"
echo "   • Top provas: $TOP PDFs por dia"
echo "======================================================================"
echo ""

# Verifica se o ano está disponível
log_info "Verificando disponibilidade do ano $ANO no INEP..."

if ! python3 _00_enem_config.py --year "$ANO" > /dev/null 2>&1; then
    log_warning "Não foi possível verificar disponibilidade (pode ser problema de rede)"
    log_info "Continuando mesmo assim..."
fi

# ==================== DEFINIÇÃO DE CAMINHOS ====================

DIR_ORIGEM="${ANO}/PROVAS E GABARITOS"
DIR_DESTINO_ROOT="ENEM/${ANO}"
DIR_DESTINO_PROVAS="${DIR_DESTINO_ROOT}/PROVAS_E_GABARITOS"

# ==================== ETAPA 1: DOWNLOAD E PREPARAÇÃO ====================

echo ""
echo "======================================================================"
echo "📥 ETAPA 1/5: DOWNLOAD E PREPARAÇÃO"
echo "======================================================================"

if [ ! -d "$ANO" ]; then
    log_info "Baixando dados do ENEM $ANO..."
    python3 _01_enem_download.py "$ANO"
    log_success "Download concluído"
else
    log_success "Dados já existem localmente"
fi

# Valida estrutura
log_info "Validando estrutura de pastas..."
python3 _00_enem_config.py --validate "$ANO"

# ==================== ETAPA 2: LIMPEZA DE PROVAS ====================

echo ""
echo "======================================================================"
echo "🧹 ETAPA 2/5: LIMPEZA E SELEÇÃO DE PROVAS"
echo "======================================================================"

if [ ! -d "$DIR_ORIGEM" ]; then
    log_error "Diretório de provas não encontrado: $DIR_ORIGEM"
fi

log_info "Selecionando top $TOP provas por dia (baseado em amostra)..."
python3 _01_limpar_provas.py "$ANO" "$TOP"
log_success "Seleção concluída"

# ==================== ETAPA 3: GERAÇÃO DE MAPAS E JSONS ====================

echo ""
echo "======================================================================"
echo "🗺️  ETAPA 3/5: GERAÇÃO DE MAPAS E METADADOS"
echo "======================================================================"

log_info "Gerando mapa de provas (R → JSON)..."
python3 _02a_gerar_mapa_provas.py "$ANO"

log_info "Convertendo itens para JSON (CSV → JSON)..."
python3 _02b_csv2json.py "$ANO"

log_info "Adicionando estrutura de imagens..."
python3 _02c_addJson.py "$ANO" "$AMOSTRA"

log_success "Metadados gerados"

# ==================== ETAPA 4: ESTATÍSTICAS E TRI ====================

echo ""
echo "======================================================================"
echo "📊 ETAPA 4/5: ANÁLISE ESTATÍSTICA E TRI"
echo "======================================================================"

log_info "Extraindo matrizes de resposta (amostra: $AMOSTRA)..."
python3 _03_enem2matriz.py "$ANO" "$AMOSTRA"

log_info "Calculando parâmetros TRI (Modelo 3PL)..."
# muito lento para grandes amostras
#python3 _04_matriz2TRI.py "$ANO"

log_info "Gerando gráficos (CCI e Boxplot)..."
# muito lento para grandes amostras
#python3 _05_matriz2graficos.py "$ANO"

log_success "Análises concluídas"

# ==================== ETAPA 5: PROCESSAMENTO DE PDFs ====================

echo ""
echo "======================================================================"
echo "📄 ETAPA 5/5: PROCESSAMENTO DE PROVAS (PDF → HTML)"
echo "======================================================================"

mkdir -p "$DIR_DESTINO_PROVAS/imagens"

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

LIMITE=$((2 * TOP))  # Usa o mesmo valor de TOP para limitar processamento
COUNT=0
    
log_info "Processando até $LIMITE PDFs..."

for PDF_PATH in $(find "${DIR_ORIGEM}" -name "*.pdf" | sort); do
    
    COUNT=$((COUNT + 1))

    if [ "$COUNT" -gt "$LIMITE" ]; then
        log_info "Limite de $LIMITE arquivos atingido"
        break
    fi

    NOME_ARQUIVO=$(basename "$PDF_PATH")
    ID_PROVA="${NOME_ARQUIVO%.*}" 
    
    echo ""
    echo "──────────────────────────────────────────────────────────────────"
    log_info "Processando ($COUNT/$LIMITE): $ID_PROVA"
    
    DIR_IMAGENS_ESPECIFICO="${DIR_DESTINO_PROVAS}/imagens/${ID_PROVA}"
    ARQUIVO_HTML_FINAL="${DIR_DESTINO_PROVAS}/${ID_PROVA}_INTERATIVO.html"

    # Fatiamento (PDF → PNGs)
    log_info "Convertendo PDF para imagens..."
    ./_06_processar_enem.sh "$PDF_PATH" "$DIR_IMAGENS_ESPECIFICO"
    
    # Montagem do HTML Interativo
    log_info "Gerando HTML interativo..."
    ./_07_montar_prova_interativa.sh "$ANO" "$ID_PROVA" "$DIR_IMAGENS_ESPECIFICO" "$ARQUIVO_HTML_FINAL"
    
    log_success "Prova processada: $ID_PROVA"
done

IFS=$SAVEIFS

# ==================== ETAPA 6: ÍNDICES ====================

echo ""
echo "======================================================================"
echo "📑 ETAPA 6/6: GERAÇÃO DE ÍNDICES"
echo "======================================================================"

log_info "Gerando índice do ano $ANO..."
python3 _08_createIndex.py "$ANO"

log_info "Atualizando índice principal..."
python3 _09_createMainIndex.py

log_success "Índices criados"

# ==================== RESUMO FINAL ====================

echo ""
echo "======================================================================"
echo "✅ PIPELINE CONCLUÍDO COM SUCESSO!"
echo "======================================================================"
echo ""
echo "📂 Arquivos gerados em: ENEM/${ANO}/"
echo ""
echo "🌐 Para visualizar:"
echo "   1. Inicie servidor local:"
echo "      python -m http.server 8000"
echo ""
echo "   2. Acesse no navegador:"
echo "      http://localhost:8000/ENEM/index.html"
echo "      http://localhost:8000/ENEM/${ANO}/index.html"
echo ""
echo "📊 Estatísticas:"
echo "   • Amostra processada: $AMOSTRA participantes"
echo "   • Provas mantidas: $TOP por dia"
echo "   • Total de PDFs processados: $COUNT"
echo ""
echo "======================================================================"

exit 0