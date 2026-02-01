"""
=====================================================================
Sistema de Configuração e Detecção Automática de Dados ENEM
Uso: python _00_enem_config.py [--check-all] [--year YEAR]

Mantém configuração centralizada e descobre automaticamente novos anos
disponíveis no site do INEP.
=====================================================================
"""

import json
import os
import sys
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from typing import Dict, List, Optional

# ==================== CONFIGURAÇÃO CENTRALIZADA ====================

class ENEMConfig:
    """Configuração centralizada do pipeline ENEM"""
    
    # Estrutura de pastas (template)
    ESTRUTURA_PASTAS = {
        'root': '{ano}',
        'inputs': '{ano}/INPUTS',
        'dados': '{ano}/DADOS',
        'provas': '{ano}/PROVAS E GABARITOS',
        'output_root': 'ENEM/{ano}',
        'output_dados': 'ENEM/{ano}/DADOS',
        'output_provas': 'ENEM/{ano}/PROVAS_E_GABARITOS',
        'output_imagens': 'ENEM/{ano}/PROVAS_E_GABARITOS/imagens',
    }
    
    # URLs conhecidas (mapeamento histórico)
    URLS_CONHECIDAS = {
        '2024': 'https://download.inep.gov.br/microdados/microdados_enem_2024.zip',
        '2023': 'https://download.inep.gov.br/microdados/microdados_enem_2023.zip',
        '2022': 'https://download.inep.gov.br/microdados/microdados_enem_2022.zip',
        '2021': 'https://download.inep.gov.br/microdados/microdados_enem_2021.zip',
        '2020': 'https://download.inep.gov.br/microdados/microdados_enem_2020.zip',
        '2019': 'https://download.inep.gov.br/microdados/microdados_enem_2019.zip',
        '2018': 'https://download.inep.gov.br/microdados/microdados_enem2018.zip',
        '2017': 'https://download.inep.gov.br/microdados/microdados_enem2017.zip',
    }
    
    # Padrões de URL possíveis (para descoberta automática)
    URL_PATTERNS = [
        'https://download.inep.gov.br/microdados/microdados_enem_{ano}.zip',
        'https://download.inep.gov.br/microdados/microdados_enem{ano}.zip',
    ]
    
    # Configurações padrão do pipeline
    DEFAULTS = {
        'amostra_padrao': 2000,
        'top_provas_padrao': 2,
        'limite_pdfs_padrao': 2,
        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    }
    
    # Arquivos esperados (para validação)
    # Suporta o padrão antigo (MICRODADOS_ENEM_2023.csv) e o novo (RESULTADOS_2024.csv)
    ARQUIVOS_ESPERADOS = {
        'microdados': [
            'MICRODADOS_ENEM_{ano}.csv', 
            'RESULTADOS_{ano}.csv'
        ],
        'itens': 'ITENS_PROVA_{ano}.csv',
        'mapa_provas': 'mapa_provas.json',
    }
    
    @classmethod
    def get_url(cls, ano: str) -> str:
        """Retorna URL para o ano especificado"""
        if ano in cls.URLS_CONHECIDAS:
            return cls.URLS_CONHECIDAS[ano]
        
        # Tenta padrões conhecidos
        return cls.URL_PATTERNS[0].format(ano=ano)
    
    @classmethod
    def get_pastas(cls, ano: str) -> Dict[str, str]:
        """Retorna estrutura de pastas para o ano"""
        return {k: v.format(ano=ano) for k, v in cls.ESTRUTURA_PASTAS.items()}
    
    @classmethod
    def salvar_config(cls, filepath: str = 'enem_config.json'):
        """Salva configuração em arquivo JSON"""
        # Ordena as URLs em ordem decrescente
        urls_ordenadas = dict(sorted(
            cls.URLS_CONHECIDAS.items(),
            key=lambda x: x[0],
            reverse=True
        ))
        
        config = {
            'urls': urls_ordenadas,
            'url_patterns': cls.URL_PATTERNS,
            'defaults': cls.DEFAULTS,
            'estrutura_pastas': cls.ESTRUTURA_PASTAS,
            'ultima_atualizacao': datetime.now().isoformat(),
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuração salva em: {filepath}")
    
    @classmethod
    def carregar_config(cls, filepath: str = 'enem_config.json'):
        """Carrega configuração de arquivo JSON"""
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'urls' in config:
                cls.URLS_CONHECIDAS.update(config['urls'])
            
            print(f"✅ Configuração carregada de: {filepath}")
            return True
        except Exception as e:
            print(f"⚠️  Erro ao carregar config: {e}")
            return False


# ==================== DESCOBERTA AUTOMÁTICA ====================

class ENEMDiscovery:
    """Descobre automaticamente novos anos disponíveis"""
    
    @staticmethod
    def get_ssl_context():
        """Cria contexto SSL permissivo"""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    
    @staticmethod
    def check_url_exists(url: str, timeout: int = 10) -> bool:
        """Verifica se URL existe"""
        headers = {'User-Agent': ENEMConfig.DEFAULTS['user_agent']}
        ctx = ENEMDiscovery.get_ssl_context()
        
        try:
            req = urllib.request.Request(url, method='HEAD', headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response:
                return response.status == 200
        except (urllib.error.HTTPError, urllib.error.URLError, Exception):
            return False
    
    @classmethod
    def descobrir_ano(cls, ano: str) -> Optional[str]:
        """Tenta descobrir URL válida para um ano específico"""
        print(f"🔍 Procurando dados para {ano}...")
        
        # Tenta URL conhecida primeiro
        if ano in ENEMConfig.URLS_CONHECIDAS:
            url = ENEMConfig.URLS_CONHECIDAS[ano]
            if cls.check_url_exists(url):
                print(f"   ✅ Encontrado (URL conhecida)")
                return url
        
        # Tenta padrões
        for pattern in ENEMConfig.URL_PATTERNS:
            url = pattern.format(ano=ano)
            print(f"   Testando: {url}")
            if cls.check_url_exists(url):
                print(f"   ✅ Encontrado!")
                # Atualiza configuração
                ENEMConfig.URLS_CONHECIDAS[ano] = url
                return url
        
        print(f"   ❌ Não encontrado")
        return None
    
    @classmethod
    def descobrir_anos_disponiveis(cls, ano_inicial: int = 2009, 
                                   ano_final: Optional[int] = None) -> Dict[str, str]:
        """Descobre todos os anos disponíveis em um intervalo"""
        if ano_final is None:
            ano_final = datetime.now().year
        
        print(f"\n{'='*70}")
        print(f"DESCOBERTA AUTOMÁTICA DE ANOS DISPONÍVEIS ({ano_inicial}-{ano_final})")
        print(f"{'='*70}\n")
        
        disponiveis = {}
        
        for ano in range(ano_inicial, ano_final + 1):
            ano_str = str(ano)
            url = cls.descobrir_ano(ano_str)
            if url:
                disponiveis[ano_str] = url
        
        print(f"\n{'='*70}")
        print(f"RESUMO: {len(disponiveis)} anos encontrados")
        print(f"{'='*70}")
        
        for ano, url in sorted(disponiveis.items()):
            print(f"  ✅ {ano}: {url}")
        
        return disponiveis


# ==================== VALIDAÇÃO DE AMBIENTE ====================

class ENEMValidator:
    """Valida ambiente e dependências"""
    
    @staticmethod
    def validar_estrutura_pastas(ano: str) -> bool:
        """Verifica se estrutura de pastas está correta"""
        pastas = ENEMConfig.get_pastas(ano)
        
        print(f"\n📁 Validando estrutura de pastas para {ano}...")
        
        obrigatorias = ['root', 'dados', 'provas']
        todas_ok = True
        
        for key in obrigatorias:
            pasta = pastas[key]
            existe = os.path.exists(pasta)
            status = "✅" if existe else "❌"
            print(f"   {status} {pasta}")
            if not existe:
                todas_ok = False
        
        return todas_ok
    
    @staticmethod
    def validar_arquivos(ano: str) -> Dict[str, bool]:
        """Verifica quais arquivos esperados existem"""
        pastas = ENEMConfig.get_pastas(ano)
        resultados = {}
        
        print(f"\n📄 Validando arquivos para {ano}...")
        
        # Microdados - Suporta o padrão legado e o novo padrão 2024+
        microdados_paths = [
            os.path.join(pastas['dados'], f'MICRODADOS_ENEM_{ano}.csv'),
            os.path.join(pastas['root'], 'DADOS', f'MICRODADOS_ENEM_{ano}.csv'),
            os.path.join(pastas['dados'], f'RESULTADOS_{ano}.csv'),  # Novo padrão
            os.path.join(pastas['root'], 'DADOS', f'RESULTADOS_{ano}.csv') # Novo padrão (raiz)
        ]
        resultados['microdados'] = any(os.path.exists(p) for p in microdados_paths)
        
        # Itens
        itens_paths = [
            os.path.join(pastas['dados'], f'ITENS_PROVA_{ano}.csv'),
            os.path.join(pastas['root'], 'DADOS', f'ITENS_PROVA_{ano}.csv'),
        ]
        resultados['itens'] = any(os.path.exists(p) for p in itens_paths)
        
        # Mapa de provas
        mapa_paths = [
            os.path.join(pastas['output_dados'], 'mapa_provas.json'),
            os.path.join(pastas['dados'], 'mapa_provas.json'),
        ]
        resultados['mapa_provas'] = any(os.path.exists(p) for p in mapa_paths)
        
        for arquivo, existe in resultados.items():
            status = "✅" if existe else "❌"
            print(f"   {status} {arquivo}")
        
        return resultados


# ==================== CLI ====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Gerenciador de Configuração ENEM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python _00_enem_config.py --check-all          # Descobre todos os anos
  python _00_enem_config.py --year 2024          # Verifica ano específico
  python _00_enem_config.py --validate 2020      # Valida ambiente para 2020
  python _00_enem_config.py --save-config        # Salva configuração atual
        """
    )
    
    parser.add_argument('--check-all', action='store_true',
                       help='Descobre todos os anos disponíveis (2009-atual)')
    parser.add_argument('--year', type=str,
                       help='Verifica disponibilidade de ano específico')
    parser.add_argument('--validate', type=str,
                       help='Valida ambiente para ano específico')
    parser.add_argument('--save-config', action='store_true',
                       help='Salva configuração atual em JSON')
    parser.add_argument('--load-config', action='store_true',
                       help='Carrega configuração de JSON')
    
    args = parser.parse_args()
    
    # Carrega config se existir
    ENEMConfig.carregar_config()
    
    if args.save_config:
        ENEMConfig.salvar_config()
        return
    
    if args.load_config:
        if ENEMConfig.carregar_config():
            print("\nURLs conhecidas:")
            for ano, url in sorted(ENEMConfig.URLS_CONHECIDAS.items()):
                print(f"  {ano}: {url}")
        return
    
    if args.check_all:
        disponiveis = ENEMDiscovery.descobrir_anos_disponiveis()
        # Atualiza e salva configuração
        ENEMConfig.URLS_CONHECIDAS.update(disponiveis)
        ENEMConfig.salvar_config()
        return
    
    if args.year:
        url = ENEMDiscovery.descobrir_ano(args.year)
        if url:
            print(f"\n✅ Ano {args.year} está disponível!")
            print(f"   URL: {url}")
            print(f"\nPara processar este ano, execute:")
            print(f"   ./_00_all.sh {args.year} 2000 2")
        else:
            print(f"\n❌ Ano {args.year} não encontrado no INEP")
            print(f"\n💡 Verifique manualmente em:")
            print(f"   https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem")
        return
    
    if args.validate:
        ano = args.validate
        print(f"\n{'='*70}")
        print(f"VALIDAÇÃO DE AMBIENTE - ENEM {ano}")
        print(f"{'='*70}")
        
        # Valida estrutura
        pastas_ok = ENEMValidator.validar_estrutura_pastas(ano)
        
        # Valida arquivos
        arquivos = ENEMValidator.validar_arquivos(ano)
        
        print(f"\n{'='*70}")
        if pastas_ok and all(arquivos.values()):
            print("✅ AMBIENTE COMPLETO E PRONTO!")
        elif pastas_ok:
            print("⚠️  ESTRUTURA OK, MAS FALTAM ARQUIVOS")
            print("\nExecute o pipeline para gerar os arquivos faltantes:")
            print(f"   ./_00_all.sh {ano} 2000 2")
        else:
            print("❌ ESTRUTURA INCOMPLETA")
            print("\nBaixe os dados primeiro:")
            print(f"   python _01_enem_download.py {ano}")
        print(f"{'='*70}")
        return
    
    # Sem argumentos: mostra ajuda
    parser.print_help()


if __name__ == "__main__":
    main()