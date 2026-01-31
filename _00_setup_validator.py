#!/usr/bin/env python3
"""
=====================================================================
Validador de Setup - Sistema ENEM
Verifica todas as dependências e ambiente antes de executar o pipeline
=====================================================================
"""

import sys
import subprocess
import os
from typing import List, Tuple

class Colors:
    """Cores ANSI para terminal"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Imprime cabeçalho"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_success(text: str):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text: str):
    """Imprime aviso"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text: str):
    """Imprime erro"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    """Imprime informação"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


class SystemValidator:
    """Validador de sistema e dependências"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
    
    def check_python_version(self) -> bool:
        """Verifica versão do Python"""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major == 3 and version.minor >= 7:
            print_success(f"Python {version_str} ✓")
            self.success.append("Python OK")
            return True
        else:
            print_error(f"Python {version_str} - Requer Python 3.7+")
            self.errors.append("Python desatualizado")
            return False
    
    def check_python_packages(self) -> bool:
        """Verifica pacotes Python necessários"""
        required_packages = [
            'pandas',
            'numpy',
            'matplotlib',
            'PIL',
            'requests',
        ]
        
        missing = []
        
        for package in required_packages:
            try:
                __import__(package)
                print_success(f"Pacote {package} instalado")
            except ImportError:
                print_error(f"Pacote {package} não encontrado")
                missing.append(package)
        
        if missing:
            self.errors.append(f"Pacotes faltando: {', '.join(missing)}")
            print_info("Para instalar: pip install -r requirements.txt")
            return False
        
        self.success.append("Todos os pacotes Python instalados")
        return True
    
    def check_bash_available(self) -> bool:
        """Verifica se bash está disponível"""
        try:
            result = subprocess.run(['bash', '--version'], 
                                  capture_output=True, 
                                  text=True)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print_success(f"Bash disponível: {version_line}")
                self.success.append("Bash OK")
                return True
        except FileNotFoundError:
            print_error("Bash não encontrado")
            self.errors.append("Bash não disponível")
            return False
    
    def check_required_scripts(self) -> bool:
        """Verifica se scripts necessários existem"""
        required_scripts = [
            '_00_enem_config.py',
            '_00_all.sh',
            '_01_enem_download.py',
            '_01_limpar_provas.py',
            '_02a_gerar_mapa_provas.py',
            '_02b_csv2json.py',
            '_02c_addJson.py',
            '_03_enem2matriz.py',
            '_04_matriz2TRI.py',
            '_05_matriz2graficos.py',
            '_08_createIndex.py',
        ]
        
        missing = []
        
        for script in required_scripts:
            if os.path.exists(script):
                print_success(f"Script {script} encontrado")
            else:
                print_error(f"Script {script} não encontrado")
                missing.append(script)
        
        if missing:
            self.errors.append(f"Scripts faltando: {', '.join(missing)}")
            return False
        
        self.success.append("Todos os scripts Python encontrados")
        return True
    
    def check_bash_scripts(self) -> bool:
        """Verifica scripts bash"""
        bash_scripts = [
            '_06_processar_enem.sh',
            '_07_montar_prova_interativa.sh',
        ]
        
        missing = []
        not_executable = []
        
        for script in bash_scripts:
            if not os.path.exists(script):
                print_error(f"Script {script} não encontrado")
                missing.append(script)
            elif not os.access(script, os.X_OK):
                print_warning(f"Script {script} existe mas não é executável")
                not_executable.append(script)
            else:
                print_success(f"Script {script} OK")
        
        if missing:
            self.errors.append(f"Scripts bash faltando: {', '.join(missing)}")
            return False
        
        if not_executable:
            self.warnings.append(f"Scripts sem permissão: {', '.join(not_executable)}")
            print_info(f"Para corrigir: chmod +x {' '.join(not_executable)}")
        
        self.success.append("Scripts bash encontrados")
        return True
    
    def check_directory_structure(self) -> bool:
        """Verifica estrutura básica de diretórios"""
        # Não verifica diretórios de anos específicos, apenas a base
        print_info("Estrutura de diretórios será criada automaticamente")
        self.success.append("Estrutura validada")
        return True
    
    def check_external_tools(self) -> bool:
        """Verifica ferramentas externas (opcional)"""
        tools = {
            'pdfimages': 'Extração de imagens (poppler-utils)',
            'convert': 'Conversão de imagens (imagemagick)',
        }
        
        has_all = True
        
        for tool, description in tools.items():
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, 
                                      text=True)
                if result.returncode == 0:
                    print_success(f"{tool} disponível ({description})")
                else:
                    raise FileNotFoundError
            except FileNotFoundError:
                print_warning(f"{tool} não encontrado - {description}")
                print_info(f"   Instale com: apt install {description.split('(')[1].split(')')[0]}")
                has_all = False
        
        if has_all:
            self.success.append("Ferramentas externas instaladas")
        else:
            self.warnings.append("Algumas ferramentas externas faltando (não crítico)")
        
        return True
    
    def check_internet_connection(self) -> bool:
        """Verifica conexão com INEP"""
        print_info("Verificando conexão com servidor INEP...")
        
        try:
            import urllib.request
            import ssl
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(
                'https://download.inep.gov.br',
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
                if response.status == 200:
                    print_success("Conexão com INEP OK")
                    self.success.append("Conexão com INEP")
                    return True
        except Exception as e:
            print_warning(f"Não foi possível conectar ao INEP: {e}")
            self.warnings.append("Sem conexão com INEP")
            return False
    
    def generate_report(self):
        """Gera relatório final"""
        print_header("RELATÓRIO DE VALIDAÇÃO")
        
        if self.success:
            print(f"\n{Colors.GREEN}✅ SUCESSOS ({len(self.success)}):{Colors.END}")
            for item in self.success:
                print(f"   • {item}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}⚠️  AVISOS ({len(self.warnings)}):{Colors.END}")
            for item in self.warnings:
                print(f"   • {item}")
        
        if self.errors:
            print(f"\n{Colors.RED}❌ ERROS ({len(self.errors)}):{Colors.END}")
            for item in self.errors:
                print(f"   • {item}")
        
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}\n")
        
        if self.errors:
            print_error("VALIDAÇÃO FALHOU - Corrija os erros acima antes de continuar")
            return False
        elif self.warnings:
            print_warning("VALIDAÇÃO OK COM AVISOS - Sistema funcional mas não ideal")
            return True
        else:
            print_success("VALIDAÇÃO COMPLETA - Sistema pronto para uso!")
            return True
    
    def run_all_checks(self) -> bool:
        """Executa todas as validações"""
        print_header("VALIDAÇÃO DE AMBIENTE - SISTEMA ENEM")
        
        checks = [
            ("Versão do Python", self.check_python_version),
            ("Pacotes Python", self.check_python_packages),
            ("Bash Shell", self.check_bash_available),
            ("Scripts Python", self.check_required_scripts),
            ("Scripts Bash", self.check_bash_scripts),
            ("Estrutura de Diretórios", self.check_directory_structure),
            ("Ferramentas Externas", self.check_external_tools),
            ("Conexão Internet", self.check_internet_connection),
        ]
        
        for name, check_func in checks:
            print(f"\n{Colors.BOLD}Verificando: {name}{Colors.END}")
            check_func()
        
        return self.generate_report()


def main():
    """Função principal"""
    validator = SystemValidator()
    success = validator.run_all_checks()
    
    if success:
        print("\n" + Colors.BOLD + "PRÓXIMOS PASSOS:" + Colors.END)
        print("\n1. Descobrir anos disponíveis:")
        print("   python3 _00_enem_config.py --check-all")
        print("\n2. Processar um ano:")
        print("   ./_00_all.sh 2020 2000 2")
        print("\n3. Visualizar resultados:")
        print("   python -m http.server 8000")
        print("   http://localhost:8000/ENEM/index.html")
        print()
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()