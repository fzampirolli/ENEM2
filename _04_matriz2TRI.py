import sys
import subprocess
import os
import glob
from datetime import datetime

# Obter o ano da linha de comando
ano = sys.argv[1] if len(sys.argv) > 1 else "2019"

# --- CAMINHOS ---
input_dir = f"./ENEM/{ano}/DADOS/MATRIZ"
# ----------------

pattern = f"{input_dir}/*.csv"
all_files = glob.glob(pattern)

# Filtrar arquivos cujo TRI ainda não existe e ignorar arquivos _TRI já gerados
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

# Código R (Mantido igual, mas a string de regex foi ajustada para segurança)
r_script = f"""
# Função para instalar pacotes se necessário
ensure_package <- function(pkg) {{
    if (!require(pkg, character.only = TRUE)) {{
        cat(sprintf("INSTALLING:%s\\n", pkg))
        install.packages(pkg, repos = "https://cloud.r-project.org/", quiet = FALSE)
        if (!require(pkg, character.only = TRUE)) {{
            stop(paste("Falha ao instalar pacote:", pkg))
        }}
    }}
}}

tryCatch({{
    ensure_package("ltm")
    ensure_package("irtoys")
    ensure_package("data.table")
}}, error = function(e) {{
    cat(sprintf("FATAL_ERROR:Erro na instalacao de pacotes: %s\\n", e$message))
    quit(save="no", status=1)
}})

suppressMessages({{
  library(ltm)
  library(irtoys)
  library(data.table)
}})

setDTthreads(1) # Usar 1 thread para evitar conflitos em subprocessos simples

# Busca na pasta ENEM/ANO/DADOS/MATRIZ
path_pattern <- "./ENEM/{ano}/DADOS/MATRIZ/*.csv"
all_files <- Sys.glob(path_pattern)
# Filtra arquivos que terminam com _TRI.csv
file_list <- all_files[!grepl("_TRI\\\\.csv$", all_files)]

total <- length(file_list)
cat(sprintf("TOTAL_FILES_R:%d\\n", total))

process_file <- function(f, i, total) {{
  cat(sprintf("PROGRESS:%d/%d\\n", i, total))
  cat(sprintf("FILE:%s\\n", basename(f)))
  
  tryCatch({{
    data <- fread(f, showProgress = FALSE)
    
    if(ncol(data) < 5) stop("Menos de 5 itens na prova")
    if(nrow(data) < 100) stop("Menos de 100 respondentes")

    data_matrix <- as.matrix(data)
    
    # TPM (3PL)
    m3PL <- tpm(data_matrix, type = "latent.trait", IRT.param = TRUE, 
                max.guessing = 0.3, 
                control = list(iter.em = 150))
    
    coeffs_raw <- coef(m3PL)
    
    # Organizar output
    result_df <- data.frame(matrix(ncol = 3, nrow = nrow(coeffs_raw)))
    colnames(result_df) <- c("Discrimination", "Difficulty", "Guessing")
    rownames(result_df) <- rownames(coeffs_raw)
    
    cols <- colnames(coeffs_raw)
    if("Dscrmn" %in% cols) {{
        result_df$Discrimination <- coeffs_raw[, "Dscrmn"]
        result_df$Difficulty     <- coeffs_raw[, "Dffclt"]
        result_df$Guessing       <- coeffs_raw[, "Gussng"]
    }} else {{
        result_df$Discrimination <- coeffs_raw[, 3]
        result_df$Difficulty     <- coeffs_raw[, 2]
        result_df$Guessing       <- coeffs_raw[, 1]
    }}
    
    output_file <- sub("\\\\.csv$", "_TRI.csv", f)
    fwrite(result_df, file = output_file, row.names = TRUE)
    
    cat(sprintf("MODEL:3PL\\n"))
    cat(sprintf("SUCCESS:%s\\n", basename(output_file)))
    
  }}, error = function(e) {{
    cat(sprintf("ERROR:%s\\n", e$message))
  }})
}}

if (total > 0) {{
    for (i in 1:total) {{
      process_file(file_list[i], i, total)
    }}
}} else {{
    cat("WARNING: R nao encontrou arquivos para processar.\\n")
}}
"""

script_path = f"_temp_tri_{ano}.R"
with open(script_path, 'w') as f:
    f.write(r_script)

try:
    # Executa o R capturando stdout e stderr
    process = subprocess.Popen(
        ['Rscript', '--vanilla', script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Ler stdout linha por linha em tempo real
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            line = line.strip()
            # Mostra o que está acontecendo (inclusive erros de instalação)
            if line.startswith("INSTALLING:"):
                print(f"📦 Instalando pacote R: {line.split(':')[1]}")
            elif line.startswith("PROGRESS:"):
                parts = line.split(":")[1].split("/")
                print(f"[{parts[0]}/{parts[1]}]", end=" ", flush=True)
            elif line.startswith("FILE:"):
                print(f"📄 {line.split(':',1)[1]}", end=" ", flush=True)
            elif line.startswith("SUCCESS:"):
                print("✅")
            elif line.startswith("ERROR:") or line.startswith("FATAL_ERROR:"):
                print(f"\n❌ {line}")
            elif line.startswith("TOTAL_FILES_R:"):
                print(f"[R] Arquivos vistos pelo R: {line.split(':')[1]}")
            else:
                # Imprime linhas desconhecidas para debug
                print(f"[R log] {line}")

    # Captura o erro final (stderr) se houver
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        print(f"\n🔴 O R terminou com erro (código {process.returncode}).")
        if stderr:
            print(f"--- LOG DE ERRO (STDERR) ---\n{stderr}\n----------------------------")
    elif stderr:
        # Às vezes o R escreve warnings no stderr mesmo com sucesso
        print(f"\n⚠️ Avisos do R (stderr):\n{stderr}")

except Exception as e:
    print(f"\n❌ Erro crítico no Python: {e}")
    
finally:
    if os.path.exists(script_path):
        os.remove(script_path)
