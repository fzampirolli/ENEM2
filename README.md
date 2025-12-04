# Sistema Automatizado de Processamento ENEM

Sistema completo e escalável para processamento automático de dados do ENEM, seguindo boas práticas de engenharia de software.

## 🎯 Características

- ✅ **Configuração Centralizada**: Todas as URLs e padrões em um único lugar
- ✅ **Descoberta Automática**: Detecta automaticamente novos anos disponíveis
- ✅ **Validação de Ambiente**: Verifica estrutura de pastas e arquivos
- ✅ **Pipeline Parametrizável**: Controle total sobre amostra e quantidade de provas
- ✅ **Logging Informativo**: Mensagens claras e coloridas
- ✅ **Tratamento de Erros**: Interrompe execução em caso de falha

## 📋 Pré-requisitos

```bash
# 1. Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 2. Instalar dependências
pip install -r requirements.txt
```

## 🚀 Uso Rápido

### 1. Descobrir Anos Disponíveis

```bash
# Verifica todos os anos (2009-atual)
python3 _00_enem_config.py --check-all

# Verifica ano específico
python3 _00_enem_config.py --year 2024
```

### 2. Processar um Ano

```bash
# Usando padrões (amostra=2000, top=2)
./_00_all.sh 2020

# Personalizando amostra e quantidade de provas
./_00_all.sh 2020 5000 4
```

### 3. Validar Ambiente

```bash
# Verifica se tudo está OK para um ano
python3 _00_enem_config.py --validate 2020
```

## 📁 Estrutura do Projeto

```
ENEM2/
├── _00_enem_config.py          # ⭐ Gerenciador de configuração
├── _00_all.sh                  # ⭐ Pipeline principal (v2)
├── _01_enem_download.py        # Download de microdados
├── _01_limpar_provas.py        # Seleção de provas por amostra
├── _02a_gerar_mapa_provas.py   # Geração de mapa de provas
├── _02b_csv2json.py            # Conversão de itens
├── _02c_addJson.py             # Estrutura de imagens
├── _03_enem2matriz.py          # Extração de matrizes
├── _04_matriz2TRI.py           # Cálculo TRI
├── _05_matriz2graficos.py      # Geração de gráficos
├── _06_processar_enem.sh       # Processamento de PDFs
├── _07_montar_prova_interativa.sh  # Geração de HTML
├── _08_createIndex.py          # Índice por ano
├── _09_createMainIndex.py      # Índice geral
├── enem_config.json            # ⭐ Configuração persistente
└── requirements.txt            # Dependências Python
```

## 🔧 Configuração Avançada

### Arquivo `enem_config.json`

O sistema gera automaticamente um arquivo de configuração:

```json
{
  "urls": {
    "2024": "https://download.inep.gov.br/microdados/...",
    "2023": "https://download.inep.gov.br/microdados/..."
  },
  "url_patterns": [
    "https://download.inep.gov.br/microdados/microdados_enem_{ano}.zip"
  ],
  "defaults": {
    "amostra_padrao": 2000,
    "top_provas_padrao": 2,
    "limite_pdfs_padrao": 2
  }
}
```

### Personalizar Padrões

Edite `_00_enem_config.py` para modificar:

- **URLs conhecidas**: `URLS_CONHECIDAS`
- **Padrões de URL**: `URL_PATTERNS`
- **Valores padrão**: `DEFAULTS`

## 📊 Pipeline Completo

O pipeline executa 6 etapas automaticamente:

### Etapa 1: Download e Preparação
- Download dos microdados do INEP
- Extração do ZIP
- Validação da estrutura

### Etapa 2: Limpeza de Provas
- Análise de amostra por cor
- Ranking de provas mais respondidas
- Seleção dos TOP N PDFs por dia
- Remoção automática de gabaritos e versões especiais

### Etapa 3: Geração de Mapas
- Extração de códigos de prova (R → JSON)
- Conversão de itens (CSV → JSON)
- Estruturação de metadados

### Etapa 4: Análise Estatística
- Extração de matrizes de resposta
- Cálculo de parâmetros TRI (3PL)
- Geração de gráficos (CCI, Boxplot)

### Etapa 5: Processamento de PDFs
- Conversão PDF → PNG
- Geração de HTML interativo
- Otimização de imagens

### Etapa 6: Índices
- Geração de índice por ano
- Atualização do índice principal

## 🎓 Exemplos Práticos

### Processar ENEM 2020 Completo

```bash
# Com amostra grande e todas as provas
./_00_all.sh 2020 10000 6
```

### Teste Rápido (Desenvolvimento)

```bash
# Amostra pequena, poucas provas
./_00_all.sh 2020 500 1
```

### Produção (Análise Completa)

```bash
# Amostra representativa, provas principais
./_00_all.sh 2020 5000 4
```

## 🔍 Troubleshooting

### Erro: "Ano não encontrado"

```bash
# 1. Verifique disponibilidade
python3 _00_enem_config.py --year 2025

# 2. Confira site do INEP
# https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem

# 3. Adicione URL manualmente em enem_config.json
```

### Erro: "Estrutura incompleta"

```bash
# Valide o ambiente
python3 _00_enem_config.py --validate 2020

# Se faltar algo, baixe novamente
python3 _01_enem_download.py 2020
```

### Erro: "Vetores não encontrados"

```bash
# O script tenta múltiplos arquivos .R
# Verifique se existem arquivos em:
ls -la 2020/INPUTS/*.R

# Se necessário, verifique formato do arquivo R
```

## 🧪 Testes

### Verificar Sistema

```bash
# 1. Teste de descoberta
python3 _00_enem_config.py --check-all

# 2. Teste de download
python3 _01_enem_download.py 2019

# 3. Teste de validação
python3 _00_enem_config.py --validate 2019

# 4. Teste de pipeline (modo rápido)
./_00_all.sh 2019 100 1
```

## 📈 Escalabilidade

### Para Adicionar Novo Ano (Automático)

```bash
# O sistema detecta automaticamente
python3 _00_enem_config.py --check-all

# Processa o ano encontrado
./_00_all.sh 2025 2000 2
```

### Para Adicionar Novo Ano (Manual)

1. Adicione URL em `enem_config.json`:
```json
{
  "urls": {
    "2025": "https://download.inep.gov.br/microdados/..."
  }
}
```

2. Execute o pipeline normalmente:
```bash
./_00_all.sh 2025 2000 2
```

## 🎨 Visualização

Após processar, visualize os resultados:

```bash
# Inicie servidor local
python -m http.server 8000

# Acesse:
# http://localhost:8000/ENEM/index.html
# http://localhost:8000/ENEM/2020/index.html
```

## 📝 Logs

O sistema gera logs informativos com cores:

- 🔵 **INFO**: Informações gerais
- 🟢 **SUCCESS**: Operações concluídas
- 🟡 **WARNING**: Avisos (não críticos)
- 🔴 **ERROR**: Erros (interrompe execução)

## 🤝 Contribuindo

Para adicionar novos recursos:

1. **Novos formatos de URL**: Adicione em `URL_PATTERNS`
2. **Novos validadores**: Estenda `ENEMValidator`
3. **Novos anos**: Sistema detecta automaticamente

## 📄 Licença

GNU Affero General Public License (AGPL-3.0)

## 👤 Autores

Francisco de Assis Zampirolli - UFABC
Irineu Antunes Jr. - UFABC

---

**Versão**: 2.0 (Automatizada)  
**Última atualização**: Dezembro 2024