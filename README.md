# 🎓 ENEM Interativo v2.0

> **Pipeline de Big Data Educacional para processamento escalável dos microdados do ENEM (1998–2025)**

Sistema completo que realiza desde a ingestão de dados brutos do INEP até a modelagem via Teoria de Resposta ao Item (TRI), gerando uma interface web interativa para análise pedagógica (validados 2019-2024).

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Novidades v2.0](#-novidades-da-versão-20)
- [Arquitetura](#%EF%B8%8F-arquitetura)
- [Instalação](#-instalação)
- [Uso Rápido](#-uso-rápido)
- [Pipeline Completo](#-pipeline-completo)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Entendendo o ENEM](#-entendendo-os-cadernos-do-enem)
- [Exemplos Práticos](#-exemplos-práticos)
- [Troubleshooting](#-troubleshooting)
- [Contribuindo](#-contribuindo)

---

## 🌟 Visão Geral

### O que este projeto faz?

Este sistema automatiza todo o processamento dos microdados do ENEM, transformando dados brutos em uma plataforma web interativa com:

- ✅ **Análise Estatística Avançada**: Modelagem TRI (Teoria de Resposta ao Item) com parâmetros 3PL
- ✅ **Interface Web Moderna**: Dashboard interativo para exploração de provas e estatísticas
- ✅ **Processamento Escalável**: Suporta arquivos de +10GB com otimização de memória
- ✅ **Automatização Completa**: Pipeline end-to-end com etapas integradas

### Para quem é este projeto?

- 📊 **Pesquisadores Educacionais**: Análise de dados do ENEM com rigor estatístico
- 👨‍🏫 **Professores**: Recursos para preparação de alunos
- 🎓 **Estudantes**: Compreensão aprofundada das provas
- 💻 **Desenvolvedores**: Base para aplicações educacionais

---

## ✨ Novidades da Versão 2.0

### 🚀 Performance e Eficiência

| Recurso | Benefício |
|---------|-----------|
| **Processamento Incremental** | Scripts ignoram arquivos já gerados (CSV, FIGS, HTML), economizando horas |
| **Inteligência de Ranking** | Foca nas provas com maior volume de respostas (Top N) |
| **Otimização de Memória** | Leitura via streaming (chunks) para arquivos de +10GB |

### 🎯 Funcionalidades Avançadas

- ✅ **Configuração Centralizada**: Todas as URLs e padrões em um único lugar (`enem_config.json`)
- ✅ **Descoberta Automática**: Detecta novos anos disponíveis no INEP
- ✅ **Validação de Ambiente**: Verifica estrutura de pastas e arquivos antes da execução
- ✅ **Pipeline Parametrizável**: Controle total sobre amostra e quantidade de provas
- ✅ **Logging Informativo**: Mensagens coloridas e claras para acompanhamento
- ✅ **Tratamento de Erros**: Interrupção controlada em caso de falha

### 🎨 Interface e UX

- ✅ **Layout Unificado**: Dashboard moderno compartilhado entre Landing Page, Estatísticas e Provas
- ✅ **Diferenciação P1/P2**: Tratamento distinto para aplicações regulares e reaplicações

---

## 🏗️ Arquitetura

### Estratégia de Três Unidades

O sistema utiliza uma arquitetura resiliente que maximiza throughput e preserva o SSD:

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE SISTEMA (SSD)                  │
│                  /usr/local/lib/ENEM2/                      │
│         Código-fonte + Ambiente Virtual + Lógica            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─────────────────────┐
                              │                     │
                              ▼                     ▼
┌───────────────────────────────────┐  ┌──────────────────────────────────┐
│  WORKSPACE (HDD 2)                │  │  STORAGE (HDD 1)                 │
│  /mnt/disco2/                     │  │  /mnt/disco1/                    │
│  • Extração de ZIPs               │  │  • Resultados finais             │
│  • Arquivos temporários           │  │  • Servidos via Apache/Web       │
│  • Alta rotatividade              │  │  • Persistência de dados         │
└───────────────────────────────────┘  └──────────────────────────────────┘
```

> 💡 **Flexibilidade**: O sistema detecta automaticamente os volumes `/mnt/disco1` e `/mnt/disco2`. Caso não encontrados, opera em **Modo Single-Disk** na pasta raiz.

### Fluxo de Dados

```
INEP → Download (HDD2) → Processamento (SSD) → Armazenamento (HDD1) → Web
```

---

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8+
- Git
- ImageMagick
- R (para scripts de análise)
- Espaço em disco: ~50GB por ano processado

### Passo a Passo

#### 1️⃣ Clonagem do Repositório

```bash
cd /usr/local/lib
sudo git clone https://github.com/fzampirolli/ENEM2
sudo chown -R $USER:$USER ENEM2
cd ENEM2
```

#### 2️⃣ Ambiente Virtual Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3️⃣ Configuração de Permissões

Para gerenciar links simbólicos sem `sudo`:

```bash
sudo chown -R $USER:$USER /mnt/disco1 /mnt/disco2 /usr/local/lib/ENEM2
```

#### 4️⃣ Verificação da Instalação

```bash
# Valida a instalação
python3 _00_enem_config.py --validate 2020

# Verifica anos disponíveis
python3 _00_enem_config.py --check-all
```

---

## 🚀 Uso Rápido

### 1️⃣ Descobrir Anos Disponíveis

```bash
# Verifica todos os anos (2009-atual)
python3 _00_enem_config.py --check-all

# Verifica ano específico
python3 _00_enem_config.py --year 2024
```

### 2️⃣ Processar um Ano

```bash
# Sintaxe
./_00_all.sh <ANO> [AMOSTRA] [TOP_PROVAS]

# Usando padrões (amostra=2000, top=2)
./_00_all.sh 2020

# Personalizando amostra e quantidade de provas
./_00_all.sh 2020 5000 4
```

**Parâmetros:**
- **ANO**: Ano do ENEM a processar (ex: 2020)
- **AMOSTRA**: Número de participantes aleatórios para cálculo estatístico (padrão: 2000)
- **TOP**: Quantidade de provas por dia com mais participantes (padrão: 2)

### 3️⃣ Validar Ambiente

```bash
# Verifica se tudo está OK para um ano
python3 _00_enem_config.py --validate 2020
```

---

## 📊 Pipeline Completo

O pipeline automatizado gerencia 6 etapas críticas de forma sequencial:

### Visão Geral das Etapas

| # | Etapa | Responsabilidade | Tecnologia |
|---|-------|------------------|------------|
| 1 | **Ingestão** | Download do ZIP para o HDD 2 e linkagem dinâmica | Python / `urllib` |
| 2 | **Limpeza** | Filtragem das provas mais relevantes baseada em amostra | Python |
| 3 | **Mapeamento** | Conversão de itens (CSV) e provas (R) para metadados JSON | Python / JSON |
| 4 | **Estatística** | Extração de matrizes e modelagem TRI (3PL) com gráficos CCI | Python / IRT Models |
| 5 | **Interface** | Conversão PDF → Imagem e montagem do HTML interativo | Shell / ImageMagick |
| 6 | **Indexação** | Atualização dos índices anuais e do portal principal | Python |

### Detalhamento das Etapas

#### 🔹 Etapa 1: Download e Preparação
```bash
python3 _01_enem_download.py <ANO>
```
- Download dos microdados do INEP
- Extração do ZIP
- Validação da estrutura
- Criação de links simbólicos

#### 🔹 Etapa 2: Limpeza de Provas
```bash
python3 _01_limpar_provas.py <ANO> <AMOSTRA> <TOP>
```
- Análise de amostra por cor de caderno
- Ranking de provas mais respondidas
- Seleção dos TOP N PDFs por dia
- Remoção automática de gabaritos e versões especiais
- **Diferenciação P1/P2**: Identifica aplicações regulares vs reaplicações

#### 🔹 Etapa 3: Geração de Mapas
```bash
python3 _02a_gerar_mapa_provas.py <ANO>
python3 _02b_csv2json.py <ANO>
python3 _02c_addJson.py <ANO>
```
- Extração de códigos de prova (R → JSON)
- Conversão de itens (CSV → JSON)
- Estruturação de metadados

#### 🔹 Etapa 4: Análise Estatística
```bash
python3 _03_enem2matriz.py <ANO> <AMOSTRA>
python3 _04_matriz2TRI.py <ANO>
python3 _05_matriz2graficos.py <ANO>
```
- Extração de matrizes de resposta (0/1)
- Cálculo de parâmetros TRI (3PL): discriminação, dificuldade, acerto ao acaso
- Geração de gráficos (CCI, Boxplot, distribuições)

#### 🔹 Etapa 5: Processamento de PDFs
```bash
./_06_processar_enem.sh <ANO>
./_07_montar_prova_interativa.sh <ANO>
```
- Conversão PDF → PNG de alta qualidade
- Geração de HTML interativo
- Otimização de imagens
- Integração com dados estatísticos

#### 🔹 Etapa 6: Índices
```bash
python3 _08_createIndex.py
python3 _09_createMainIndex.py
```
- Geração de índice por ano
- Atualização do índice principal
- Criação de landing page

---

## 📁 Estrutura do Projeto

```
ENEM2/
├── 📋 Scripts de Configuração
│   ├── _00_enem_config.py          # ⭐ Gerenciador de configuração
│   ├── _00_all.sh                  # ⭐ Pipeline principal (v2)
│   └── enem_config.json            # ⭐ Configuração persistente
│
├── 📥 Etapa 1: Ingestão
│   └── _01_enem_download.py        # Download com criação automática de links
│
├── 🧹 Etapa 2: Limpeza
│   └── _01_limpar_provas.py        # Seleção de provas por amostra
│
├── 🗺️ Etapa 3: Mapeamento
│   ├── _02a_gerar_mapa_provas.py   # Geração de mapa de provas
│   ├── _02b_csv2json.py            # Conversão de itens
│   └── _02c_addJson.py             # Estrutura de imagens
│
├── 📊 Etapa 4: Estatística
│   ├── _03_enem2matriz.py          # Extração de matrizes
│   ├── _04_matriz2TRI.py           # Cálculo TRI
│   └── _05_matriz2graficos.py      # Geração de gráficos
│
├── 🖼️ Etapa 5: Interface
│   ├── _06_processar_enem.sh       # Processamento de PDFs
│   └── _07_montar_prova_interativa.sh  # Geração de HTML
│
├── 📑 Etapa 6: Indexação
│   ├── _08_createIndex.py          # Índice por ano
│   └── _09_createMainIndex.py      # Índice geral
│
├── 📦 Dependências
│   └── requirements.txt            # Dependências Python
│
└── 🔗 Links Simbólicos
    ├── ENEM -> /mnt/disco1/ENEM/   # ⭐ Storage (HDD 1)
    ├── 2021 -> /mnt/disco2/2021/   # ⭐ Workspace (HDD 2)
    └── microdados_enem_2021.zip -> /mnt/disco2/microdados_enem_2021.zip
```

---

## 📚 Entendendo os Cadernos do ENEM

### ✅ Definição Completa

**P1, P2, P3... = APLICAÇÕES DIFERENTES (cada aplicação tem Dia 1 e Dia 2, com várias cores de prova por dia, onda cada cor é uma prova diferente)**

```
P1 = Aplicação principal/oficial
P2 = 1ª Reaplicação (provas diferentes da P1)
P3 = 2ª Reaplicação (provas diferentes)
```

### 📋 Estrutura de Cada Aplicação

Cada aplicação possui:
- **Dia 1**: Caderno com LC (inglês questões 01-05 e espanhol 1-5) + CH (90 questões)
- **Dia 2**: Caderno com CN + MT (90 questões)

Cada dia tem múltiplas cores de caderno (ordem das questões varia):
- 🟦 AZUL
- ⬜ BRANCO
- 🟨 AMARELO
- ⬛ CINZA
- 🟪 ROSA
- 🟩 VERDE

### Padrão utilizado nas numerações das questões

| Bloco | Fatia |  Chave JSON |
|---|---|---|
| Inglês (D1) | q1–q5 |  `"1"`…`"5"` |
| Espanhol (D1) | q01–q05 |  `"01"`…`"05"` |
| LC (D1) | q06–q45 | `"06"`…`"45"` |
| CH (D1) | q46–q90 | `"46"`…`"90"` |
| CN+MT (D2) | q91–q180 |  `"91"`…`"180"` |

### 🔍 Exemplo Prático

```
ENEM_2022_P1_CAD_03_DIA_1_BRANCO.pdf  ← Aplicação OFICIAL, Dia 1, BRANCO (LC+CH)
ENEM_2022_P2_CAD_03_DIA_1_BRANCO.pdf  ← REAPLICAÇÃO, Dia 1, BRANCO (LC+CH diferentes!)
ENEM_2022_P1_CAD_06_DIA_2_CINZA.pdf   ← Aplicação OFICIAL, Dia 2, CINZA (CN+MT)
ENEM_2022_P2_CAD_06_DIA_2_CINZA.pdf   ← REAPLICAÇÃO, Dia 2, CINZA (CN+MT diferentes!)
```

### 🎯 Com TOP=2

Seleciona a **1 APLICAÇÃO** (P1) com mais respondentes:

**Dia 1:**
- P1 (aplicação oficial - BRANCO - LC+CH em um PDF): ~5 milhões de alunos ✅
- P1 (aplicação oficial - CINZA - LC+CH em um PDF): ~5 milhões de alunos ✅

**Dia 2:**
- P1 (aplicação oficial - ROSA - CN+MT em um PDF): ~5 milhões de alunos ✅
- P1 (aplicação oficial - VERDE - CN+MT em um PDF): 5 milhões de alunos ✅

**Total: 4 PDFs** (1 aplicação × 2 dias) + múltiplas cores = 4 cadernos

---

## 💡 Exemplos Práticos

### 🚀 Cenário 1: Teste Rápido (Desenvolvimento)

Ideal para testar o pipeline sem consumir muitos recursos:

```bash
# Amostra pequena, poucas provas
./_00_all.sh 2020 100 1

# Tempo estimado: ~30 minutos
# Espaço em disco: ~5GB
```

### 📊 Cenário 2: Análise Padrão

Configuração recomendada para análises educacionais:

```bash
# Amostra representativa, provas principais
./_00_all.sh 2020 2000 2

# Tempo estimado: ~2 horas
# Espaço em disco: ~5GB
```

### 🎓 Cenário 3: Análise Completa (Pesquisa)

Para pesquisas acadêmicas com rigor estatístico:

```bash
# Amostra grande, todas as aplicações
./_00_all.sh 2020 10000 6

# Tempo estimado: ~6 horas
# Espaço em disco: ~5GB
```

### 📈 Cenário 4: Produção (Análise Abrangente)

Configuração balanceada para produção:

```bash
# Amostra representativa, provas principais
./_00_all.sh 2020 5000 4

# Tempo estimado: ~4 horas
# Espaço em disco: ~5GB
```

---

## 🔧 Configuração Avançada

### Arquivo `enem_config.json`

O sistema gera automaticamente este arquivo após a primeira execução:

```json
{
  "urls": {
    "2024": "https://download.inep.gov.br/microdados/microdados_enem_2024.zip",
    "2023": "https://download.inep.gov.br/microdados/microdados_enem_2023.zip",
    "2022": "https://download.inep.gov.br/microdados/microdados_enem_2022.zip"
  },
  "url_patterns": [
    "https://download.inep.gov.br/microdados/microdados_enem_{ano}.zip",
    "https://download.inep.gov.br/microdados/enem_{ano}/microdados_enem_{ano}.zip"
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

```python
# URLs conhecidas (anos testados)
URLS_CONHECIDAS = {
    "2024": "https://...",
    "2023": "https://...",
}

# Padrões de URL para anos desconhecidos
URL_PATTERNS = [
    "https://download.inep.gov.br/microdados/microdados_enem_{ano}.zip",
]

# Valores padrão
DEFAULTS = {
    "amostra_padrao": 2000,
    "top_provas_padrao": 2,
}
```

---

## 🔍 Troubleshooting

### ❌ Erro: "Ano não encontrado"

**Problema**: URL do ano não está configurada

```bash
# 1. Verifique disponibilidade no INEP
python3 _00_enem_config.py --year 2025

# 2. Confira manualmente o site
# https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem

# 3. Adicione URL manualmente em enem_config.json
{
  "urls": {
    "2025": "https://download.inep.gov.br/microdados/microdados_enem_2025.zip"
  }
}
```

### ❌ Erro: "Estrutura incompleta"

**Problema**: Arquivos necessários não foram baixados corretamente

```bash
# Valide o ambiente
python3 _00_enem_config.py --validate 2020

# Se faltar algo, baixe novamente
python3 _01_enem_download.py 2020

# Verifique arquivos extraídos
ls -la /mnt/disco2/2020/
```

### ❌ Erro: "Vetores não encontrados"

**Problema**: Arquivos .R com códigos de prova não localizados

```bash
# O script tenta múltiplos arquivos .R
# Verifique se existem em:
ls -la 2020/INPUTS/*.R

# Arquivos esperados:
# - VETORES_PROVA_RESPOSTAS_*.R
# - vetores_*.R
```

### ❌ Erro: Permission Denied

**Problema**: Falta de permissões para criar links simbólicos

```bash
# Conceda permissões
sudo chown -R $USER:$USER /mnt/disco1 /mnt/disco2 /usr/local/lib/ENEM2

# Verifique permissões
ls -la /mnt/disco1 /mnt/disco2
```

### ❌ Erro: Out of Memory

**Problema**: Sistema sem memória suficiente

```bash
# Reduza o tamanho da amostra
./_00_all.sh 2020 500 2

# Ou aumente swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 🧪 Testes

### Verificação Completa do Sistema

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

### Teste de Incrementalidade

```bash
# Execute o pipeline
./_00_all.sh 2020 1000 2

# Interrompa com Ctrl+C

# Execute novamente - deve pular arquivos já processados
./_00_all.sh 2020 1000 2
```

---

## 📈 Escalabilidade

### Adicionar Novo Ano (Automático)

```bash
# O sistema detecta automaticamente
python3 _00_enem_config.py --check-all

# Processa o ano encontrado
./_00_all.sh 2025 2000 2
```

### Adicionar Novo Ano (Manual)

1. **Adicione URL em `enem_config.json`**:
```json
{
  "urls": {
    "2025": "https://download.inep.gov.br/microdados/microdados_enem_2025.zip"
  }
}
```

2. **Execute o pipeline**:
```bash
./_00_all.sh 2025 2000 2
```

### Processar Múltiplos Anos

```bash
# Script bash para processar vários anos
for ano in 2019 2020 2021 2022 2023 2024; do
    echo "Processando ENEM $ano..."
    ./_00_all.sh $ano 2000 2
done
```

Ou, em uma única linha e considerando default para amostras e top: `2000 2`:

```bash
for ano in {2019..2024}; do ./_00_all.sh $ano 2000 4; done
```

Ou,

```bash
nohup bash -c 'for ano in {2019..2024}; do ./_00_all.sh $ano 2000 4; done' &
```

Para verificar o processo de execução, digite `tail -f nohup.out`.

---

## 🎨 Visualização

### Iniciar Servidor Local

```bash
# Navegue até a pasta de outputs
cd /mnt/disco1

# Inicie servidor HTTP
python3 -m http.server 8000
```

### Acessar Interface

Abra seu navegador em:

- **Página Principal**: `http://localhost:8000/ENEM/index.html`
- **Ano Específico**: `http://localhost:8000/ENEM/2020/index.html`
- **Estatísticas**: `http://localhost:8000/ENEM/2020/estatisticas.html`
- **Prova Interativa**: `http://localhost:8000/ENEM/2020/provas/DIA_1/...`

---

## 📝 Logs

O sistema gera logs informativos com código de cores:

```
🔵 INFO: Informações gerais do processo
🟢 SUCCESS: Operações concluídas com sucesso
🟡 WARNING: Avisos (não críticos, mas importante observar)
🔴 ERROR: Erros que interrompem a execução
```

### Exemplo de Log

```
🔵 [INFO] Iniciando pipeline para ENEM 2020
🔵 [INFO] Parâmetros: AMOSTRA=2000, TOP=2
🟢 [SUCCESS] Download concluído: microdados_enem_2020.zip
🔵 [INFO] Processando limpeza de provas...
🟡 [WARNING] Arquivo GABARITO.pdf removido automaticamente
🟢 [SUCCESS] 4 provas selecionadas para processamento
🔵 [INFO] Iniciando análise TRI...
🟢 [SUCCESS] Pipeline concluído em 2h 15min
```

---

## 🤝 Contribuindo

### Como Adicionar Novos Recursos

#### 1. Novos Formatos de URL
Adicione em `_00_enem_config.py`:
```python
URL_PATTERNS = [
    "https://download.inep.gov.br/microdados/microdados_enem_{ano}.zip",
    "https://novo-padrao.inep.gov.br/enem/{ano}/dados.zip",  # Novo
]
```

#### 2. Novos Validadores
Estenda a classe `ENEMValidator`:
```python
class ENEMValidator:
    def validar_novo_formato(self, ano):
        # Sua lógica aqui
        pass
```

#### 3. Novas Etapas no Pipeline
Adicione no `_00_all.sh`:
```bash
# Etapa 7: Sua nova funcionalidade
echo "🔹 Etapa 7: Processando nova funcionalidade..."
python3 _10_nova_funcionalidade.py $ANO
```

### Diretrizes

- Mantenha a compatibilidade com o sistema incremental
- Adicione testes para novas funcionalidades
- Documente mudanças no README
- Use logging colorido para feedback ao usuário

---

## 📄 Licença

**GNU Affero General Public License (AGPL-3.0)**

Este projeto é software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da AGPL-3.0.

---

## 👤 Autores

**Francisco de Assis Zampirolli**  
Universidade Federal do ABC (UFABC)

📧 Email: [contato@exemplo.com]  
🔗 GitHub ENEM v2: [github.com/fzampirolli/ENEM2](https://github.com/fzampirolli/ENEM2)
🔗 GitHub ENEM v1: [github.com/fzampirolli/ENEM](https://github.com/fzampirolli/ENEM)

---

## 🙌 Agradecimentos

Agradecemos especialmente ao **Professor Irineu Antunes Jr.**, cuja parceria, incentivo e discussões construtivas contribuíram significativamente para a evolução desta versão automatizada do projeto.

---

## 📊 Estatísticas do Projeto

| Métrica | Valor |
|---------|-------|
| **Anos Suportados** | 1998 - 2025 (28 anos) |
| **Scripts Python** | 15 |
| **Scripts Shell** | 4 |
| **Linhas de Código** | ~5.000 |
| **Dependências** | 12 bibliotecas |
| **Tempo Médio de Processamento** | 2-6 horas/ano |
| **Espaço em Disco** | 15-40 GB/ano |

---

## 🔗 Links Úteis

- 📚 **Documentação INEP**: [www.gov.br/inep](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem)
- 📊 **Teoria de Resposta ao Item**: [Wikipedia TRI](https://pt.wikipedia.org/wiki/Teoria_de_resposta_ao_item)
- 🐍 **Python IRT Models**: [PyPI](https://pypi.org/search/?q=irt)
- 🖼️ **ImageMagick**: [imagemagick.org](https://imagemagick.org/)

---

<div align="center">

**📌 Versão 2.0 (Automatizada)**  
**🗓️ Última atualização: Janeiro 2026**

⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!

[⬆️ Voltar ao topo](#-enem-interativo-v20)

</div>