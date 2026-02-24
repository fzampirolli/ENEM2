#!/bin/bash
# ==============================================================================
# SCRIPT: _07_montar_prova_interativa.sh
# DESCRIÇÃO: Gera o HTML interativo com distinção Inglês/Espanhol.
# CORREÇÃO: 
#   - Detecta Dia 1.
#   - Inglês (1º bloco 1-5): ID sem zero ("1"). Label "Resp. 1".
#   - Espanhol (2º bloco 1-5): ID com zero ("01"). Label "Resp. 01".
#   - LC (6-9): ID com zero ("06"). Label "Resp. 06".
# ==============================================================================

ANO="$1"
ID_PROVA="$2"
DIR_IMGS="$3"
HTML_FILE="$4"

if [ -z "$HTML_FILE" ]; then
    echo "❌ Erro: Argumentos faltando."
    exit 1
fi

# ==================== VERIFICAÇÃO DE EXISTÊNCIA ====================
if [ -f "$HTML_FILE" ]; then
    echo "   [PULAR] HTML Interativo já existe: $(basename "$HTML_FILE")"
    exit 0
fi
# ===================================================================

REL_IMG_PATH="imagens/$(basename "$DIR_IMGS")"

echo "   [HTML] Gerando arquivo: $(basename "$HTML_FILE")"

cat > "$HTML_FILE" <<EOF
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8"/>
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ENEM $ANO - $ID_PROVA</title>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<link rel="stylesheet" href="../../_cronometro.css">
<script src="../../_quiz2.ok.js?v=$(date +%s)"></script>

<style>
    body { background-color: #808080; margin: 0; padding: 0; font-family: sans-serif; }
    #page-container { background-color: white; margin: 0 auto; padding: 0; max-width: 1000px; box-shadow: 0px 0px 15px rgba(0,0,0,0.5); min-height: 100vh; padding-bottom: 50px; }
    .fatia-imagem { width: 100%; height: auto; display: block; margin: 0; padding: 0; }
    .questao-wrapper { position: relative; height: 80px; width: 100%; margin-top: 5px; margin-bottom: 15px; }
    .barra-resposta { color: black; position: absolute; top: 0px; left: 0px; font-size: normal; background-color: lightgreen; width: 100%; height: 50px; }
    @media (max-width: 600px) { .barra-resposta table { transform: scale(0.9); transform-origin: left top; } }
</style>
</head>
<body id="${ID_PROVA}">
<div class="cronometro" style="position: sticky; top: 0; z-index: 9999;">
<table style="width: 100%;"><thead><tr>
<th style="font-size: small; background-color: lightgreen; width: 50%; text-align:center;">
<h1><a href="../../">ENEM Interativo</a></h1>
<p style="font-size: x-small; margin:0;">$ID_PROVA</p>
</th>
<th style="font-size: small; background-color: lightgreen; width: 40%; text-align:left;">
<div id="contador"><div class="reloj" id="Horas">00</div><div class="reloj" id="Minutos">:00</div><div class="reloj" id="Segundos">:00</div></div>
<div id="botoes"><input type="button" class="boton" id="inicio" value=" &#9658;" onclick="inicio();"><input type="button" class="boton" id="parar" value=" &#8718;" onclick="parar();" disabled=""><input type="button" class="boton" id="continuar" value=" &#8634;" onclick="inicio();" disabled=""></div>
</th></tr></thead></table></div>
<div id="page-container">
EOF

# Variáveis de Estado para o Loop
Q01_COUNT=0
IS_DIA_1=0

# Verifica se é Dia 1 pelo nome do arquivo
if [[ "$ID_PROVA" == *"DIA_1"* ]]; then
    IS_DIA_1=1
fi

# LOOP DE IMAGENS (Ordenado para garantir sequência Ing -> Esp)
for img_path in $(find "$DIR_IMGS" -name "*.png" | sort); do
    img_name=$(basename "$img_path")
    
    echo "  <img src=\"${REL_IMG_PATH}/${img_name}\" class=\"fatia-imagem\" loading=\"lazy\">" >> "$HTML_FILE"

    TEM_QUESTAO=$(echo "$img_name" | grep -oE '_q[0-9]+')
    EH_INI=$(echo "$img_name" | grep "_ini")

    if [ -n "$TEM_QUESTAO" ] && [ -z "$EH_INI" ]; then
        # Obtém o número bruto (ex: 01, 05, 45) e o inteiro
        Q_RAW=$(echo "$TEM_QUESTAO" | sed 's/_q//')
        Q_NUM=$((10#$Q_RAW)) # Força base 10 para evitar erro com 08/09

        # ID e Rótulo Padrão (Sem zero à esquerda para a maioria)
        Q_FINAL_ID=$(echo "$Q_RAW" | sed 's/^0*//')
        Q_LABEL="$Q_FINAL_ID"

        # Lógica Específica para DIA 1 (LC)
        if [ "$IS_DIA_1" -eq 1 ]; then
            # Controla contador de "q01" para saber se é Inglês (1º) ou Espanhol (2º)
            if [ "$Q_NUM" -eq 1 ]; then
                Q01_COUNT=$((Q01_COUNT+1))
            fi

            if [ "$Q_NUM" -le 5 ]; then
                if [ "$Q01_COUNT" -le 1 ]; then
                    # INGLÊS: 1 a 5 (Sem zero)
                    Q_FINAL_ID=$(echo "$Q_RAW" | sed 's/^0*//')
                    Q_LABEL="$Q_FINAL_ID"
                else
                    # ESPANHOL: 01 a 05 (Com zero)
                    Q_FINAL_ID="$Q_RAW" # "01"
                    Q_LABEL="$Q_RAW"
                fi
            elif [ "$Q_NUM" -le 9 ]; then
                # LC 06 a 09: Manter zero para padronizar com seu pedido "06-45"
                Q_FINAL_ID="$Q_RAW" # "06"
                Q_LABEL="$Q_RAW"
            else
                # 10 a 90: Normal (Raw já é 10, 45...)
                Q_FINAL_ID="$Q_RAW"
                Q_LABEL="$Q_RAW"
            fi
        fi

        cat >> "$HTML_FILE" <<BLOCK
        <div class="questao-wrapper" id="question${Q_FINAL_ID}">
            <form id="${Q_FINAL_ID}" class="barra-resposta">
                <table style="position: absolute; top: 12px; left: 0; width: 100%;">
                    <thead>
                        <tr>
                            <th style="width:25%; text-align:left; padding-left: 10px; font-weight: bold; font-size: 1.2em;">Resp. ${Q_LABEL}</th>
                            <th style="width:13%; text-align:left;"><input style="transform: scale(2); cursor: pointer;" type="RADIO" name="choices${Q_FINAL_ID}" value="A" onclick="checkAnswer('${Q_FINAL_ID}')"> A</th>
                            <th style="width:13%; text-align:left;"><input style="transform: scale(2); cursor: pointer;" type="RADIO" name="choices${Q_FINAL_ID}" value="B" onclick="checkAnswer('${Q_FINAL_ID}')"> B</th>
                            <th style="width:13%; text-align:left;"><input style="transform: scale(2); cursor: pointer;" type="RADIO" name="choices${Q_FINAL_ID}" value="C" onclick="checkAnswer('${Q_FINAL_ID}')"> C</th>
                            <th style="width:13%; text-align:left;"><input style="transform: scale(2); cursor: pointer;" type="RADIO" name="choices${Q_FINAL_ID}" value="D" onclick="checkAnswer('${Q_FINAL_ID}')"> D</th>
                            <th style="width:13%; text-align:left;"><input style="transform: scale(2); cursor: pointer;" type="RADIO" name="choices${Q_FINAL_ID}" value="E" onclick="checkAnswer('${Q_FINAL_ID}')"> E</th>
                        </tr>
                    </thead>
                </table>
            </form>
        </div>
BLOCK
    fi
done

cat >> "$HTML_FILE" <<EOF
<div style="padding: 20px; text-align: center; background-color: lightgreen; margin-top: 20px;">
    <button onclick="checkStatistcs(1)" style="font-size: 20px; padding: 10px 40px; background-color: lightblue; cursor: pointer; border: 2px solid #005f6b; border-radius: 5px; font-weight: bold;">
        Ver Estatísticas
    </button>
</div>
</div></body></html>
EOF

echo "   ✅ HTML Gerado com sucesso."