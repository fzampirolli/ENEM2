'''
=====================================================================
Copyright (C) 2021 UFABC, developed by Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of "ENEM Interativo".

Languages: Python 3.8.5, Javascript, HTML and many libraries
described at github.com/fzampirolli/ENEM

You should cite some references included in vision.ufabc.edu.br
in any publication about it.

ENEM Interativo is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License
(gnu.org/licenses/agpl-3.0.txt) as published by the Free Software
Foundation, either version 3 of the License, or (at your option)
any later version.

ENEM Interativo is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
=====================================================================
'''

# Sintaxe: python _enem_download.py 2024

import os
import sys
import zipfile
import urllib.request
import time
import ssl

# --- Configuração de Caminhos com Fallback Automático ---
# Tenta usar os discos montados; se não existirem, usa o diretório atual
STORAGE_BASE = "/mnt/disco1/ENEM_STORAGE"
WORKSPACE_BASE = "/mnt/disco2"

if os.path.exists(STORAGE_BASE):
    STORAGE_PATH = STORAGE_BASE
else:
    STORAGE_PATH = os.path.join(os.getcwd(), "ENEM") # Fallback local

if os.path.exists(WORKSPACE_BASE):
    WORKSPACE_PATH = WORKSPACE_BASE
else:
    WORKSPACE_PATH = os.getcwd() # Fallback local
# -------------------------------------------------------

# Mapeamento Ano -> URL
URLS_ENEM = {
    '2024': 'https://download.inep.gov.br/microdados/microdados_enem_2024.zip',
    '2023': 'https://download.inep.gov.br/microdados/microdados_enem_2023.zip',
    '2022': 'https://download.inep.gov.br/microdados/microdados_enem_2022.zip',
    '2021': 'https://download.inep.gov.br/microdados/microdados_enem_2021.zip',
    '2020': 'https://download.inep.gov.br/microdados/microdados_enem_2020.zip',
    '2019': 'https://download.inep.gov.br/microdados/microdados_enem_2019.zip',
    '2018': 'https://download.inep.gov.br/microdados/microdados_enem2018.zip',
    '2017': 'https://download.inep.gov.br/microdados/microdados_enem2017.zip',
    '2016': 'https://download.inep.gov.br/microdados/microdados_enem2016.zip',
    '2015': 'https://download.inep.gov.br/microdados/microdados_enem2015.zip',
    '2014': 'https://download.inep.gov.br/microdados/microdados_enem2014.zip',
    '2013': 'https://download.inep.gov.br/microdados/microdados_enem2013.zip',
    '2012': 'https://download.inep.gov.br/microdados/microdados_enem2012.zip',
    '2011': 'https://download.inep.gov.br/microdados/microdados_enem2011.zip',
    '2010': 'https://download.inep.gov.br/microdados/microdados_enem2010_2.zip',
    '2009': 'https://download.inep.gov.br/microdados/microdados_enem2009.zip',
    '2008': 'https://download.inep.gov.br/microdados/microdados_enem_2008.zip',
}

def get_headers_and_context():
    """Retorna headers e contexto SSL para as requisições"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    }
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    return headers, ctx

def check_file_exists(url, headers, ctx):
    """Verifica se o arquivo existe no servidor antes de baixar"""
    print(f"Verificando se o arquivo existe no servidor...")
    try:
        req = urllib.request.Request(url, method='HEAD', headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            if response.status == 200:
                print("✅ Arquivo encontrado no servidor!")
                return True
            else:
                print(f"⚠️ Status HTTP: {response.status}")
                return False
    except urllib.error.HTTPError as e:
        print(f"❌ Arquivo não encontrado (HTTP {e.code})")
        print("💡 Os microdados deste ano ainda não foram publicados pelo INEP.")
        print("💡 Verifique em: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem")
        return False
    except Exception as e:
        print(f"⚠️ Não foi possível verificar: {e}")
        print("Tentando fazer o download mesmo assim...")
        return True  # Tenta baixar mesmo com erro na verificação

def download_with_progress(url, filename, headers, ctx):
    """Faz download do arquivo com barra de progresso"""
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            total_size = int(response.info().get('Content-Length', 0).strip())
            block_size = 1024 * 8  # 8KB
            
            with open(filename, 'wb') as f:
                downloaded = 0
                start_time = time.time()
                
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Atualiza barra de progresso
                    if total_size > 0:
                        percent = min(int(downloaded * 100 / total_size), 100)
                        duration = time.time() - start_time
                        speed = int(downloaded / (1024 * duration)) if duration > 0 else 0
                        
                        bar_length = 40
                        filled_length = int(bar_length * percent // 100)
                        bar = '█' * filled_length + '-' * (bar_length - filled_length)
                        
                        sys.stdout.write(f'\rBaixando: |{bar}| {percent}% ({speed} KB/s)')
                        sys.stdout.flush()
        
        print("\nDownload concluído.")
        return True

    except urllib.error.HTTPError as e:
        print(f"\n❌ Erro HTTP {e.code}: O arquivo pode não existir ou a URL mudou.")
        return False
    except Exception as e:
        print(f"\n❌ Erro de conexão: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <ANO>")
        print(f"Exemplo: python {sys.argv[0]} 2023")
        sys.exit(1)

    ano = sys.argv[1]

    if ano not in URLS_ENEM:
        print(f"Aviso: Ano '{ano}' não mapeado explicitamente. Tentando padrão...")
        url = f'https://download.inep.gov.br/microdados/microdados_enem_{ano}.zip'
    else:
        url = URLS_ENEM[ano]

    filename = os.path.join(WORKSPACE_PATH, f"microdados_enem_{ano}.zip")
    extract_folder = os.path.join(WORKSPACE_PATH, ano)

    print(f"="*60)
    print(f"Iniciando processo para o ENEM {ano}")
    print(f"URL: {url}")
    print(f"="*60)

    # Prepara headers e contexto SSL
    headers, ctx = get_headers_and_context()

    # Verifica se o arquivo existe no servidor
    if not check_file_exists(url, headers, ctx):
        sys.exit(1)

    # 1. Download
    if not os.path.exists(filename):
        success = download_with_progress(url, filename, headers, ctx)
        if not success:
            if os.path.exists(filename): 
                os.remove(filename)  # Remove arquivo parcial
            sys.exit(1)
    else:
        print(f"Arquivo {filename} já existe. Pulando download.")

    # 2. Extração
    print(f"Extraindo para: {extract_folder}...")
    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder, exist_ok=True)

    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
    
    # 3. Automação de Links (Apenas se estiver usando discos externos)
    link_name = os.path.join(os.getcwd(), ano)
    
    # SÓ cria link se a pasta de extração for FORA da pasta do projeto
    if os.path.abspath(extract_folder) != os.path.abspath(link_name):
        if os.path.lexists(link_name):
            os.remove(link_name)
        try:
            os.symlink(extract_folder, link_name)
            print(f"✅ Link simbólico criado: {link_name} -> {extract_folder}")
        except PermissionError:
            print(f"⚠️ Aviso: Sem permissão para criar link. Use 'sudo chown -R $USER:$USER {os.getcwd()}'")
    else:
        print(f"✅ Dados extraídos localmente em: {extract_folder}")

if __name__ == "__main__":
    main()