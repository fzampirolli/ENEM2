import sys
import subprocess
import os
import glob
from datetime import datetime, timedelta

# Obter o ano da linha de comando
ano = sys.argv[1] if len(sys.argv) > 1 else "2019"

# --- CAMINHOS ATUALIZADOS ---
input_dir = f"./ENEM/{ano}/DADOS/MATRIZ"
# ----------------------------

pattern = f"{input_dir}/*.csv"
all_files = glob.glob(pattern)
# file_list = [f for f in all_files if not f.endswith("_TRI.csv")]
# Filtrar arquivos cujo TRI ainda não existe
file_list = []
for f in all_files:
    if f.endswith("_TRI.csv"):
        continue
    tri_file = f.replace(".csv", "_TRI.csv")
    if not os.path.exists(tri_file):
        file_list.append(f)

total_files = len(file_list)

print(f"=" * 60)
print(f"Processando TRI para o ano: {ano}")
print(f"Diretório: {input_dir}")
print(f"Total de arquivos a processar: {total_files}")
print(f"=" * 60)

if total_files == 0:
    print("Nenhum arquivo encontrado para processar!")
    sys.exit(0)

# Código R OTIMIZADO E CORRIGIDO
r_script = f"""
if (!require("ltm")) install.packages("ltm", repos = "https://cloud.r-project.org/", quiet = TRUE)
if (!require("irtoys")) install.packages("irtoys", repos = "https://cloud.r-project.org/", quiet = TRUE)
if (!require("data.table")) install.packages("data.table", repos = "https://cloud.r-project.org/", quiet = TRUE)

suppressMessages({{
  library(ltm)
  library(irtoys)
  library(data.table)
}})

setDTthreads(0)

# --- CAMINHO NO R ATUALIZADO ---
# Busca na pasta ENEM/ANO/DADOS/MATRIZ
all_files <- Sys.glob("./ENEM/{ano}/DADOS/MATRIZ/*.csv")
file_list <- all_files[!grepl("_TRI\\\\.csv$", all_files)]
# -------------------------------

total <- length(file_list)
cat(sprintf("TOTAL_FILES:%d\\n", total))

process_file <- function(f, i, total) {{
  start_time <- Sys.time()
  
  cat(sprintf("PROGRESS:%d/%d\\n", i, total))
  cat(sprintf("FILE:%s\\n", basename(f)))
  
  tryCatch({{
    data <- fread(f, showProgress = FALSE)
    
    # Validação mínima de dados
    if(ncol(data) < 5) stop("Menos de 5 itens na prova")
    if(nrow(data) < 100) stop("Menos de 100 respondentes")

    data_matrix <- as.matrix(data)
    
    # Tenta rodar o 3PL (TPM)
    # IRT.param = TRUE retorna (Gussng, Dffclt, Dscrmn)
    m3PL <- tpm(data_matrix, type = "latent.trait", IRT.param = TRUE, 
                max.guessing = 0.3, # Trava chute máximo em 30%
                control = list(iter.em = 150))
    
    # Extrai coeficientes
    # O ltm retorna nesta ordem: Guessing (1), Difficulty (2), Discrimination (3)
    coeffs_raw <- coef(m3PL)
    
    # CORREÇÃO CRÍTICA: Reordenar colunas para o padrão (a, b, c)
    # Queremos: Discrimination, Difficulty, Guessing
    
    # Verifica nomes das colunas retornadas para garantir
    cols <- colnames(coeffs_raw)
    
    # Cria dataframe vazio com número certo de linhas
    result_df <- data.frame(matrix(ncol = 3, nrow = nrow(coeffs_raw)))
    colnames(result_df) <- c("Discrimination", "Difficulty", "Guessing")
    rownames(result_df) <- rownames(coeffs_raw)
    
    # Preenche mapeando corretamente
    # Se o ltm retornou nomes, usa eles. Se não, usa índices conhecidos do ltm::tpm
    if("Dscrmn" %in% cols) {{
        result_df$Discrimination <- coeffs_raw[, "Dscrmn"]
        result_df$Difficulty     <- coeffs_raw[, "Dffclt"]
        result_df$Guessing       <- coeffs_raw[, "Gussng"]
    }} else {{
        # Fallback por índice (Padrão ltm: 1=Guess, 2=Diff, 3=Discr)
        result_df$Discrimination <- coeffs_raw[, 3]
        result_df$Difficulty     <- coeffs_raw[, 2]
        result_df$Guessing       <- coeffs_raw[, 1]
    }}
    
    model_used <- "3PL"
    output_file <- sub("\\\\.csv$", "_TRI.csv", f)
    fwrite(result_df, file = output_file, row.names = TRUE)
    
    cat(sprintf("MODEL:%s\\n", model_used))
    cat(sprintf("SUCCESS:%s\\n", basename(output_file)))
    
    return(model_used)
    
  }}, error = function(e) {{
    cat(sprintf("ERROR:%s\\n", e$message))
    return("FAILED")
  }})
}}

for (i in 1:length(file_list)) {{
  process_file(file_list[i], i, total)
}}
"""

# Salvar script R temporário
script_path = f"_temp_tri_{ano}.R"
with open(script_path, 'w') as f:
    f.write(r_script)

# Executar R
try:
    process = subprocess.Popen(
        ['Rscript', '--vanilla', script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    files_processed = 0
    start_overall = datetime.now()
    
    # Ler output linha por linha
    for line in process.stdout:
        line = line.strip()
        
        if line.startswith("PROGRESS:"):
            parts = line.split(":")[1].split("/")
            current = int(parts[0])
            total = int(parts[1])
            progress_pct = (current / total) * 100
            print(f"[{current}/{total}] {progress_pct:.1f}%", end=" | ", flush=True)
                
        elif line.startswith("FILE:"):
            filename = line.split(":", 1)[1]
            print(f"📄 {filename}", end=" ", flush=True)
            
        elif line.startswith("MODEL:"):
            model = line.split(":", 1)[1]
            print(f"🎯 {model}", end=" ", flush=True)
            
        elif line.startswith("SUCCESS:"):
            print("✅")
            
        elif line.startswith("ERROR:"):
            error = line.split(":", 1)[1]
            print(f"\n❌ {error[:60]}...")
    
    process.wait()
        
except Exception as e:
    print(f"\n❌ Erro ao executar R: {e}")
    sys.exit(1)
    
finally:
    if os.path.exists(script_path):
        os.remove(script_path)