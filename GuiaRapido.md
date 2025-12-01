# 🚀 Guia de Início Rápido - Sistema ENEM

## ⚡ Setup em 3 Minutos

### 1️⃣ Preparar Ambiente

```bash
# Clone ou acesse o diretório do projeto
# git clone https://github.com/fzampirolli/ENEM2.git
cd ENEM2

# Crie ambiente virtual Python
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instale dependências
# para atualizar: pip freeze > requirements.txt
pip install -r requirements.txt

# Dê permissão aos scripts bash
chmod +x *.sh
```

### 2️⃣ Validar Sistema

```bash
# Verifica se tudo está OK
python3 _00_setup_validator.py
```

Se aparecer `✅ VALIDAÇÃO COMPLETA - Sistema pronto para uso!`, você está pronto! 🎉

### 3️⃣ Processar um Ano

```bash
# Exemplo: ENEM 2020, usando 100 amostras e mantendo apenas 1 PDF por dia
# ATENÇÃO: todos os PDFs em ./2020/PROVAS... serão removidos, exceto 2
./_00_all.sh 2020 100 1

# Modo completo (recomendado para produção):
# 2000 amostras e até 2 PDFs por dia
./_00_all.sh 2020 2000 2
```

### 4️⃣ Visualizar Resultados

```bash
# Inicie servidor web
python -m http.server 8000

# Abra no navegador:
# http://localhost:8000/ENEM/index.html
```

---

## 📚 Entendendo os Parâmetros

```bash
./_00_all.sh <ANO> <AMOSTRA> <TOP>
```

- **ANO**: Ano do ENEM (ex: 2020)
- **AMOSTRA**: Quantidade de participantes na análise estatística
- **TOP**: Número de PDFs mais respondidos a manter por dia

### Configurações Recomendadas

| Cenário | Comando | Tempo Aprox. |
|---------|---------|--------------|
| **Teste Rápido** | `./_00_all.sh 2020 100 1` | ~30 min |
| **Desenvolvimento** | `./_00_all.sh 2020 500 1` | ~50 min |
| **Produção** | `./_00_all.sh 2020 2000 2` | ~120 min |
| **Análise Completa** | `./_00_all.sh 2020 5000 4` | ~150 min |

---

## 🔍 Descobrir Anos Disponíveis

```bash
# Ver todos os anos disponíveis no INEP
python3 _00_enem_config.py --check-all

# Verificar ano específico
python3 _00_enem_config.py --year 2024
```

---

## 🛠️ Resolução Rápida de Problemas

### ❌ "Python 3.7+ required"

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10

# Mac
brew install python@3.10
```

### ❌ "Pacotes faltando"

```bash
pip install -r requirements.txt
```

### ❌ "Permission denied: ./_00_all.sh"

```bash
chmod +x *.sh
```

### ❌ "Bash não encontrado" (Windows)

Use Git Bash ou WSL (Windows Subsystem for Linux)

### ⚠️  "Ferramentas externas faltando"

```bash
# Ubuntu/Debian
sudo apt install poppler-utils imagemagick

# Mac
brew install poppler imagemagick
```

---

## 📖 Fluxo Completo

```
┌──────────────────────────────────────────────────────────┐
│ 1. Download dos Microdados (INEP)                        │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│ 2. Seleção de Provas (Top N por amostra)                 │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│ 3. Geração de Mapas e Metadados (R→JSON, CSV→JSON)       │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│ 4. Análise Estatística (TRI, Matrizes, Gráficos)         │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│ 5. Processamento de PDFs (PDF→PNG→HTML)                  │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│ 6. Geração de Índices (HTML navegável)                   │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 Casos de Uso Comuns

### Processar Múltiplos Anos

```bash
# Opção 1: Loop manual
for ano in 2019 2020 2021; do
    ./_00_all.sh $ano 2000 2
done

# Opção 2: Script personalizado
cat > processar_varios.sh << 'EOF'
#!/bin/bash
anos=(2019 2020 2021 2022 2023)
for ano in "${anos[@]}"; do
    echo "Processando $ano..."
    ./_00_all.sh $ano 2000 2
done
EOF
chmod +x processar_varios.sh
./processar_varios.sh
```

### Reprocessar Apenas Estatísticas

```bash
# Se você já tem os dados baixados:
python3 _03_enem2matriz.py 2020 2000
python3 _04_matriz2TRI.py 2020
python3 _05_matriz2graficos.py 2020
```

### Adicionar Mais Provas a um Ano Existente

```bash
# Aumentar de 2 para 4 provas
python3 _01_limpar_provas.py 2020 4

# Reprocessar apenas as novas provas
# (ajustar LIMITE no _00_all.sh ou processar manualmente)
```

---

## 📊 Monitoramento

Durante a execução, você verá:

- 🔵 **INFO**: Progresso normal
- 🟢 **SUCCESS**: Etapa concluída
- 🟡 **WARNING**: Avisos (não crítico)
- 🔴 **ERROR**: Erro (processo interrompido)

---

## 💡 Dicas Pro

### 1. Usar tela/screen para processamento longo

```bash
# Inicia sessão
screen -S enem

# Executa pipeline
./_00_all.sh 2020 5000 4

# Desconecta (Ctrl+A, D)
# Reconecta depois
screen -r enem
```

### 2. Logs personalizados

```bash
# Salvar log completo
./_00_all.sh 2020 2000 2 2>&1 | tee enem_2020.log
```

### 3. Validação antes de processar

```bash
# Sempre valide primeiro
python3 _00_enem_config.py --validate 2020

# Depois processe
./_00_all.sh 2020 2000 2
```

---

## 🆘 Suporte

### Documentação Completa
```bash
cat README.md
```

### Validar Sistema
```bash
python3 _00_setup_validator.py
```

### Verificar Configuração
```bash
python3 _00_enem_config.py --help
```

---

## ✅ Checklist de Sucesso

Após executar o pipeline, você deve ter:

```
ENEM/
├── index.html                  ✅ Página principal do projeto
└── 2020/
    ├── index.html                  ✅ Página principal do ano
    ├── FIGS/                       ✅ Gráficos CCI e BoxPlot
    ├── DADOS/
    │   ├── mapa_provas.json        ✅ Mapeamento de códigos
    │   ├── ITENS_PROVA_2020.json   ✅ Metadados dos itens
    │   └── *.csv                   ✅ Matrizes de resposta
    └── PROVAS_E_GABARITOS/
        ├── *_INTERATIVO.html       ✅ Provas interativas
        └── imagens/                ✅ Imagens das questões
```

### Verificação Rápida

```bash
# Lista arquivos gerados
ls -lh ENEM/2020/
ls -lh ENEM/2020/DADOS/
ls -lh ENEM/2020/PROVAS_E_GABARITOS/

# Conta provas processadas
ls ENEM/2020/PROVAS_E_GABARITOS/*_INTERATIVO.html | wc -l
```

---

## 🎓 Próximos Passos

Após o primeiro processamento bem-sucedido:

1. **Explore os HTMLs gerados** no navegador
2. **Ajuste parâmetros** conforme necessidade
3. **Processe mais anos** usando os mesmos comandos
4. **Personalize scripts** para seu fluxo de trabalho

---

**Pronto! 🎉** Você agora tem um sistema completo e automatizado para processar dados do ENEM!

Para dúvidas ou problemas, verifique o README.md completo ou abra uma issue no repositório.