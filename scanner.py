#!/usr/bin/env python3
"""
🔍 SCANNER REPOSITORY - Value Stock Finder
Scansiona automaticamente tutto il repository prima dello sviluppo
"""

import os
import datetime
from pathlib import Path

def scan_repository():
    """Scansiona tutto il repository e crea report completo"""
    
    print("🔍 SCANNER REPOSITORY - Avvio scansione...")
    print("=" * 50)
    
    # File da escludere
    EXCLUDE_DIRS = {'.git', '__pycache__', 'venv', '.vscode', 'node_modules'}
    EXCLUDE_FILES = {'repository_scan.txt', 'scanner.py'}
    
    # Estensioni da includere
    INCLUDE_EXTENSIONS = {'.py', '.txt', '.md', '.json', '.yaml', '.yml', '.ini', '.cfg'}
    
    scan_content = []
    scan_content.append("=== SCANSIONE COMPLETA REPOSITORY ===")
    scan_content.append(f"Data: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    scan_content.append(f"Progetto: Value Stock Finder")
    scan_content.append("=" * 50)
    scan_content.append("")
    
    # Scansiona struttura cartelle
    scan_content.append("=== STRUTTURA CARTELLE ===")
    for root, dirs, files in os.walk('.'):
        # Filtra cartelle da escludere
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        scan_content.append(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file not in EXCLUDE_FILES:
                scan_content.append(f"{subindent}{file}")
    
    scan_content.append("")
    
    # Scansiona contenuto file
    scan_content.append("=== CONTENUTO FILE ===")
    
    for root, dirs, files in os.walk('.'):
        # Filtra cartelle da escludere
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file in EXCLUDE_FILES:
                continue
                
            file_path = Path(root) / file
            file_extension = file_path.suffix.lower()
            
            # Includi solo file di testo/codice
            if file_extension in INCLUDE_EXTENSIONS or file_extension == '':
                try:
                    relative_path = file_path.relative_to('.')
                    scan_content.append("")
                    scan_content.append(f"=== FILE: {relative_path} ===")
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().strip()
                        
                    if content:
                        scan_content.append(content)
                    else:
                        scan_content.append("(file vuoto)")
                        
                    scan_content.append(f"=== FINE: {relative_path} ===")
                    
                except Exception as e:
                    scan_content.append(f"❌ Errore lettura {file_path}: {e}")
    
    # Salva scan
    output_file = "repository_scan.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(scan_content))
    
    # Statistiche
    total_files = len([f for f in scan_content if f.startswith('=== FILE:')])
    
    print(f"✅ SCANSIONE COMPLETATA!")
    print(f"📁 File scansionati: {total_files}")
    print(f"💾 Output: {output_file}")
    print(f"📊 Dimensione: {os.path.getsize(output_file)} bytes")
    print("")
    print("🎯 ORA PUOI INCOLLARE IL CONTENUTO DI repository_scan.txt AL ASSISTENTE")
    print("=" * 50)
    
    return output_file

def quick_scan():
    """Scansione rapida solo file Python principali"""
    print("🔍 SCANSIONE RAPIDA - Solo file .py principali")
    
    python_files = []
    for root, dirs, files in os.walk('.'):
        if '.git' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    scan_content = []
    scan_content.append("=== SCANSIONE RAPIDA PYTHON ===")
    scan_content.append(f"Data: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    scan_content.append("")
    
    for py_file in sorted(python_files):
        try:
            relative_path = py_file.relative_to('.')
            scan_content.append(f"=== FILE: {relative_path} ===")
            
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            scan_content.append(content)
            scan_content.append(f"=== FINE: {relative_path} ===")
            scan_content.append("")
            
        except Exception as e:
            scan_content.append(f"❌ Errore {py_file}: {e}")
    
    output_file = "python_scan.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(scan_content))
    
    print(f"✅ Scansione rapida completata: {output_file}")
    return output_file

if __name__ == "__main__":
    print("🎯 VALUE STOCK FINDER - REPOSITORY SCANNER")
    print("Scegli modalità:")
    print("1. Scansione COMPLETA (tutti i file)")
    print("2. Scansione RAPIDA (solo Python)")
    
    choice = input("\nScelta (1-2): ").strip()
    
    if choice == "1":
        scan_repository()
    elif choice == "2":
        quick_scan()
    else:
        print("Scansione completa per default...")
        scan_repository()