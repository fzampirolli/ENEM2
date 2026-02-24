/**
 * _quiz2.js - Versão Definitiva v10
 * - Correção de Persistência em CH/CN/MT: Aplica offset (45/90/135) na chave de busca.
 * - Sincronia total entre checkAnswer (HTML) e checkStatistcs (JSON).
 */

var userAnswers = {};
var globalData = {};
var activeExams = [];
var currentYear = "";
var currentDay = "";
var currentColor = "";

// --- Inicialização ---
window.addEventListener("load", function() {
    initApp();
    inicio();
});

function initApp() {
    var body = document.getElementsByTagName("body")[0];
    if (!body) return;
    
    var bodyId = body.id; 
    var parts = bodyId.split("_");
    if (parts.length < 6) return;

    currentYear = parts[1];
    var diaIndex = parts.indexOf("DIA");
    if(diaIndex !== -1) currentDay = parts[diaIndex + 1];
    currentColor = parts[parts.length - 1]; 

    loadJSON(currentYear);
}


var globalData = {};
var globalMapa = {}; // Novo: armazena o mapa oficial
var activeExams = [];

function loadJSON(year) {
    // Carrega o mapa_provas.json PRIMEIRO
    fetch("../DADOS/mapa_provas.json")
        .then(response => response.json())
        .then(mapa => {
            globalMapa = mapa;
            // Só depois carrega os itens
            return fetch("../DADOS/ITENS_PROVA_" + year + ".json");
        })
        .then(response => response.json())
        .then(itens => {
            globalData = itens;
            filterActiveExams();
        })
        .catch(err => console.error("❌ Erro ao carregar JSONs:", err));
}

function filterActiveExams() {
    activeExams = [];
    
    // Pegamos apenas os IDs que VOCÊ definiu como corretos no mapa_provas.json
    var idsNoMapa = Object.keys(globalMapa);

    for (var i = 0; i < idsNoMapa.length; i++) {
        var id = idsNoMapa[i];
        var exam = globalData[id];

        if (exam) {
            // Normalização de cor (Branco/Branca)
            var jsonColor = (exam.COR || "").toUpperCase();
            if (jsonColor === "BRANCA") jsonColor = "BRANCO";
            if (jsonColor === "AMARELA") jsonColor = "AMARELO";

            var bodyColor = currentColor.toUpperCase();
            if (bodyColor === "BRANCA") bodyColor = "BRANCO";
            if (bodyColor === "AMARELA") bodyColor = "AMARELO";

            // Só aceita se a cor bater E o dia bater
            // Isso ignora o ID 1355 porque ele não está no globalMapa
            if (jsonColor === bodyColor && exam.DIA === currentDay) {
                activeExams.push({ id: id, area: exam.AREA, data: exam });
            }
        }
    }
    console.log("✅ Provas Ativas (Filtradas pelo Mapa):", activeExams.map(e => e.id));
}

// --- Interação ---

function checkAnswer(qId) {
    // qId vem do HTML (ex: "46", "90", "01")
    var num = parseInt(qId, 10);
    var str = qId.toString();
    var compositeKey = "";

    // Lógica de Chave de Salvamento (Idêntica à de Leitura abaixo)
    if (currentDay === "1") {
        if (num >= 46) {
            compositeKey = "CH_" + num;
        } else if (num >= 6) {
            compositeKey = "LC_" + num;
        } else {
            // LC 1-5
            if (str.length === 2 && str.charAt(0) === '0') compositeKey = "LC_ESP_" + num;
            else compositeKey = "LC_ING_" + num;
        }
    } else {
        // Dia 2
        if (num >= 136) compositeKey = "MT_" + num;
        else if (num >= 91) compositeKey = "CN_" + num;
    }
    
    var radios = document.getElementsByName("choices" + qId);
    var selected = null;

    for (var i = 0; i < radios.length; i++) {
        if (radios[i].checked) { selected = radios[i].value; break; }
    }

    if (selected) {
        userAnswers[compositeKey] = selected;
        // console.log("Salvo: " + compositeKey + " = " + selected);
        
        var btn = document.getElementById(qId);
        if (btn) {
            var oldVal = btn.value;
            btn.style.backgroundColor = "#90EE90";
            setTimeout(function(){ 
                btn.value = oldVal; 
                btn.style.backgroundColor = "lightblue"; 
            }, 500);
        }
    } else {
        alert("Selecione uma alternativa.");
    }
    registrarLog("verificou_resposta", { questao_id: qId });
}

// --- Relatório ---

function checkStatistcs(type) {
    if (activeExams.length === 0) {
        alert("Aguarde o carregamento dos dados.");
        return;
    }

    var totalCorrect = 0;
    
    var listIngles = [];
    var listEspanhol = [];
    var listLC = [];
    var listCH = [];
    var listCN = [];
    var listMT = [];
    
    var processedKeys = {}; 

    for (var k = 0; k < activeExams.length; k++) {
        var exam = activeExams[k];
        var area = exam.area;
        var questionsObj = exam.data.QUESTIONS;
        
        for (var key in questionsObj) {
            if (questionsObj.hasOwnProperty(key)) {
            //     var intKey = parseInt(key, 10);
            //     var uniqueId = "";
            //     var displayLabel = "";

            //     // --- GERAÇÃO DA CHAVE CORRETA PARA BUSCAR NO userAnswers ---
            //     // Aplica o offset necessário para alinhar JSON (1-45) com Caderno (46-90)
                
            //     if (area === "LC") {
            //         if (intKey <= 5) {
            //             // Verifica se é Espanhol ("01") ou Inglês ("1") no JSON original
            //             if (key.length === 2 && key.charAt(0) === '0') {
            //                 uniqueId = "LC_ESP_" + intKey;
            //                 displayLabel = "0" + intKey + " (Esp)";
            //                 listEspanhol.push(createItem(uniqueId, displayLabel, area, questionsObj[key], intKey));
            //             } else {
            //                 uniqueId = "LC_ING_" + intKey;
            //                 displayLabel = intKey + " (Ing)";
            //                 listIngles.push(createItem(uniqueId, displayLabel, area, questionsObj[key], intKey));
            //             }
            //         } else {
            //             uniqueId = "LC_" + intKey;
            //             displayLabel = (intKey < 10 ? "0" + intKey : intKey.toString());
            //             listLC.push(createItem(uniqueId, displayLabel, area, questionsObj[key], intKey));
            //         }
            //     } 
            //     else if (area === "CH") {
            //         // CH: JSON 1 vira 46
            //         var realNum = intKey + 45;
            //         uniqueId = "CH_" + realNum; 
            //         displayLabel = realNum.toString();
            //         listCH.push(createItem(uniqueId, displayLabel, area, questionsObj[key], intKey));
            //     }
            //     else if (area === "CN") {
            //         // CN: JSON 1 vira 91
            //         var realNum = intKey + 90;
            //         uniqueId = "CN_" + realNum;
            //         displayLabel = realNum.toString();
            //         listCN.push(createItem(uniqueId, displayLabel, area, questionsObj[key], intKey));
            //     }
            //     else if (area === "MT") {
            //         // MT: JSON 1 vira 136
            //         var realNum = intKey + 135;
            //         uniqueId = "MT_" + realNum;
            //         displayLabel = realNum.toString();
            //         listMT.push(createItem(uniqueId, displayLabel, area, questionsObj[key], intKey));
            //     }
            // 
            // --- Trecho Corrigido em _quiz2.ok.js ---

                // No loop de questionsObj:
                var intKey = parseInt(key, 10);
                var uniqueId = "";
                var displayLabel = "";

                if (area === "LC") {
                    if (intKey <= 5) {
                        if (key.length === 2 && key.charAt(0) === '0') {
                            uniqueId = "LC_ESP_" + intKey;
                            displayLabel = "0" + intKey + " (Esp)";
                            listEspanhol.push(createItem(uniqueId, displayLabel, area, questionsObj[key], intKey));
                        } else {
                            uniqueId = "LC_ING_" + intKey;
                            displayLabel = intKey + " (Ing)";
                            listIngles.push(createItem(uniqueId, displayLabel, area, questionsObj[key], intKey));
                        }
                    } else {
                        uniqueId = "LC_" + intKey;
                        displayLabel = (intKey < 10 ? "0" + intKey : intKey.toString());
                        listLC.push(createItem(uniqueId, displayLabel, area, questionsObj[key], intKey));
                    }
                } 
                else {
                    // Para CH (46-90), CN (91-135) e MT (136-180)
                    // As chaves no JSON já são os números reais do caderno
                    uniqueId = area + "_" + intKey; 
                    displayLabel = intKey.toString();
                    
                    if (area === "CH") listCH.push(createItem(uniqueId, displayLabel, area, questionsObj[key], intKey));
                    else if (area === "CN") listCN.push(createItem(uniqueId, displayLabel, area, questionsObj[key], intKey));
                    else if (area === "MT") listMT.push(createItem(uniqueId, displayLabel, area, questionsObj[key], intKey));
                }
            }
        }
    }

    // Helper para criar objeto padronizado
    function createItem(uid, label, area, data, sortIdx) {
        return {
            compositeKey: uid,
            displayLabel: label,
            area: area,
            data: data,
            sortIdx: sortIdx
        };
    }

    // Ordenação interna
    var sortFn = function(a, b) { return a.sortIdx - b.sortIdx; };
    listIngles.sort(sortFn);
    listEspanhol.sort(sortFn);
    listLC.sort(sortFn);
    listCH.sort(sortFn);
    listCN.sort(sortFn);
    listMT.sort(sortFn);

    // Montagem Final
    var finalOrder = [];
    if (currentDay === "1") {
        finalOrder = finalOrder.concat(listIngles, listEspanhol, listLC, listCH);
    } else {
        finalOrder = finalOrder.concat(listCN, listMT);
    }

    // HTML
    var cssStyle = '<style type="text/css">' +
        'body{font-family:Arial,sans-serif; padding:20px;}' +
        '.tg{border-collapse:collapse;width:100%;margin-top:20px;}' +
        '.tg td, .tg th{border:1px solid #ccc;padding:8px;text-align:center;font-size:13px;}' +
        '.tg th{background-color:#f0f0f0;font-weight:bold;}' +
        '.correct{background-color:#d4edda} .wrong{background-color:#f8d7da}' +
        'a {text-decoration:none; color:blue;} a:visited {color:purple;}' +
        '.spoiler { background-color: #333; color: #333; cursor: pointer; user-select: none; }' +
        '.spoiler:hover { background-color: #555; }' +
        '.spoiler.revealed { background-color: transparent; color: black; font-weight: bold; }' +
        '</style>';

    var scriptJS = '<script>function toggleSpoiler(cell) { cell.classList.toggle("revealed"); }</script>';

    var html = '<html><head>' + cssStyle + scriptJS + '</head><body>';
    html += '<div style="max-width:800px; margin:0 auto;">';
    html += '<button onclick="window.print()" style="float:right;margin:10px;">Imprimir</button>';
    html += '<h1>ENEM Interativo</h1>';
    html += '<p><strong>Prova:</strong> ' + currentYear + ' | <strong>Cor:</strong> ' + currentColor + '</p><hr>';

    html += '<table class="tg"><thead><tr><th>N.</th><th>Disciplina</th><th>Correta <small>(Clique)</small></th><th>Marcada</th><th>Hab.</th><th>TRI</th><th>Est.</th><th>Questão</th><th>Ajuda</th></tr></thead><tbody>';

    for (var i = 0; i < finalOrder.length; i++) {
        var item = finalOrder[i];
        
        // Busca Resposta com a CHAVE CORRETA (com Offset)
        var userAns = userAnswers[item.compositeKey] || "";
        var correctAns = item.data.answer;
        
        var rowClass = "";
        if (userAns !== "") {
            if (userAns === correctAns) {
                totalCorrect++;
                rowClass = "correct";
            } else {
                rowClass = "wrong";
            }
        }
        
        var linkTRI = "-";
        var linkBOX = "-";
        var linkQuestion = "-";
        var linkHelp = "-";
        
        // Identifica se a questão é de Espanhol pela chave composta
        var isEspanhol = (item.compositeKey.indexOf("LC_ESP_") === 0);

        if (item.data.images && item.data.images.length >= 4) {
            var triImg = item.data.images[0] || null;
            var boxImg = item.data.images[1] || null;
            var dataImg = item.data.images[2] || null;
            var helpFile = item.data.images[3] || null;

            // Se NÃO for espanhol e o arquivo existir, mostra o link "Ver"
            if (!isEspanhol) {
                if (triImg) linkTRI = '<a href="../FIGS/' + triImg + '" target="_blank">Ver</a>';
                if (boxImg) linkBOX = '<a href="../FIGS/' + boxImg + '" target="_blank">Ver</a>';
            } else {
                // Para espanhol, TRI e BOX ficam explicitamente como "-"
                linkTRI = "-";
                linkBOX = "-";
            }

            // A imagem da questão (img_data) sempre aparece para todos os idiomas
            if (dataImg) {
                linkQuestion = '<a href="../FIGS/' + dataImg + '" target="_blank">Ver</a>';
            }
            // O arquivo de ajuda (help.html) sempre aparece para todos os idiomas
            if (helpFile) {
                linkHelp = '<a href="../FIGS/' + helpFile + '" target="_blank">Ver</a>';
            }
        }

        html += '<tr class="' + rowClass + '">';
        html += '<td><b>' + item.displayLabel + '</b></td>';
        html += '<td>' + item.area + '</td>';
        html += '<td class="spoiler" onclick="toggleSpoiler(this)" title="Revelar">' + correctAns + '</td>';
        html += '<td>' + userAns + '</td>';
        html += '<td>' + (item.data.ability || "-") + '</td>';
        html += '<td>' + linkTRI + '</td>';
        html += '<td>' + linkBOX + '</td>';
        html += '<td>' + linkQuestion + '</td>';
        html += '<td>' + linkHelp + '</td>';
        html += '</tr>';
    }

    html += '</tbody></table>';
    html += '<h3>Acertos Totais: ' + totalCorrect + '</h3>';
    html += '</div></body></html>';

    var win = window.open('', '_blank', 'height=800,width=900,scrollbars=yes,resizable=yes');
    if (win) {
        win.document.write(html);
        win.document.close();
    }
}

// --- CRONÔMETRO ---
var timerInterval, startTime, elapsedTime = 0;
function inicio() { if (!timerInterval) { startTime = Date.now() - elapsedTime; timerInterval = setInterval(updateTimer, 10); toggleBtn(true); } }
function parar() { clearInterval(timerInterval); timerInterval = null; toggleBtn(false); }
function reinicio() { parar(); elapsedTime = 0; updateDisplay(0, 0, 0, 0); if(document.getElementById("inicio")) document.getElementById("inicio").disabled = false; if(document.getElementById("continuar")) document.getElementById("continuar").disabled = true; if(document.getElementById("reinicio")) document.getElementById("reinicio").disabled = true; }
function updateTimer() { var now = Date.now(); elapsedTime = now - startTime; var totalSeconds = Math.floor(elapsedTime / 1000); var h = Math.floor(totalSeconds / 3600); var m = Math.floor((totalSeconds % 3600) / 60); var s = totalSeconds % 60; updateDisplay(h, m, s, 0); }
function updateDisplay(h, m, s, cs) { try { var elH = document.getElementById("Horas"), elM = document.getElementById("Minutos"), elS = document.getElementById("Segundos"); if(elH) elH.innerText = (h < 10 ? "0" + h : h); if(elM) elM.innerText = ":" + (m < 10 ? "0" + m : m); if(elS) elS.innerText = ":" + (s < 10 ? "0" + s : s); } catch(e){} }
function toggleBtn(running) { var btnInicio = document.getElementById("inicio"), btnParar = document.getElementById("parar"), btnCont = document.getElementById("continuar"); if(btnInicio) btnInicio.disabled = running; if(btnParar) btnParar.disabled = !running; if(btnCont) btnCont.disabled = running; }