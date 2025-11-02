"""
🎯 VALUE STOCK FINDER - Main Integrator
Versione: 1.0
Data: 2024-01-15
"""

import os
import sys
sys.path.append('reporting')  
from reporting import ReportGenerator
import json
from datetime import datetime
from src.alert_system import get_alert_system

def main():
    print("🎯 VALUE STOCK FINDER - MAIN INTEGRATOR")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Verifica struttura
    if not os.path.exists('src/mio_stock_finder.py'):
        print("❌ File principale non trovato in src/")
        print("💡 Esegui prima la riorganizzazione del repository")
        return
    
    print("✅ Struttura repository verificata")
    print("\nScegli operazione:")
    print("1. 🔍 Esegui Screening Completo")
    print("2. 📊 Solo Backtesting") 
    print("3. 🏗️  Test Struttura")
    
    scelta = input("\nScelta (1-3): ").strip()
    
    if scelta == "1":
        esegui_screening()
    elif scelta == "2":
        esegui_backtesting()
    elif scelta == "3":
        test_struttura()
    else:
        print("❌ Scelta non valida")

def esegui_screening():
    """Esegue lo screening completo con sistema di alert"""
    try:
        sys.path.append('src')
        from mio_stock_finder import analizza_azioni_avanzata
        
        print("\n🚀 AVVIO SCREENING COMPLETO...")
        risultati = analizza_azioni_avanzata()
        
        # 🔥 NUOVO: SISTEMA DI ALERT
        print("\n🔍 ANALISI OPPORTUNITÀ ECCEZIONALI...")
        alert_system = get_alert_system()
        analysis_results = alert_system.analyze_opportunities(risultati)
        alert_system.generate_alerts(analysis_results)
        
        # Salva in outputs/screens/
        data_oggi = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"outputs/screens/screening_{data_oggi}.json"
        
        with open(filename, 'w') as f:
            json.dump(risultati, f, indent=2)
        
        print(f"💾 Risultati salvati in: {filename}")
        
        # Genera report screening
        print("📊 Generazione report screening...")
        report_gen = ReportGenerator()
        report_paths = report_gen.generate_comprehensive_report(risultati, [])
        print(f"📄 Report generati:")
        print(f"  - Dashboard: {report_paths['html_dashboard']}")
        print(f"  - PDF: {report_paths['pdf_report']}")
        
        return risultati
        
    except Exception as e:
        print(f"❌ Errore durante lo screening: {e}")
        return None
        
def esegui_backtesting():
    """Esegue backtesting sulle migliori opportunità - VERSIONE INTEGRATA"""
    try:
        # Importa i moduli
        sys.path.append('src')
        from backtester import backtest_opportunita, test_backtest_sistema, salva_risultati_backtest
        from mio_stock_finder import analizza_azioni_avanzata
        
        print("\n📊 MODALITÀ BACKTESTING INTEGRATA")
        print("1. Test sistema backtesting")
        print("2. Backtesting su screening reale (OGGI)")
        print("3. Backtesting su file screening precedente")
        
        scelta = input("\nScelta (1-3): ").strip()
        
        if scelta == "1":
            test_backtest_sistema()
            
        elif scelta == "2":
            print("🔍 Esecuzione screening in tempo reale...")
            
            # Esegui lo screening per ottenere opportunità REALI
            risultati_screening = analizza_azioni_avanzata()
            
            if not risultati_screening:
                print("❌ Nessun risultato dallo screening")
                return

            # ANALISI ALERT PRIMA DEL BACKTESTING
            alert_system = get_alert_system()
            analysis_results = alert_system.analyze_opportunities(risultati_screening)
            
            # Filtra solo le opportunità di qualità (come fa mio_stock_finder.py)
            min_discount = 5.0  # Stesso valore di CONFIG
            opportunita_reali = [
                r for r in risultati_screening 
                if r['sconto'] > min_discount and r['qualita_ok']
            ]
            
            if not opportunita_reali:
                print("❌ Nessuna opportunità di qualità trovata oggi")
                return
                
            print(f"🎯 Trovate {len(opportunita_reali)} opportunità di qualità")

            # MOSTRA ALERT PRIMA DEL BACKTESTING
            alert_system.generate_alerts(analysis_results)
            
            # Esegui backtesting sulle opportunità reali
            risultati_backtest = backtest_opportunita(opportunita_reali, anni=3)
            
            if risultati_backtest:
                salva_risultati_backtest(risultati_backtest)
    
                # NUOVO: GENERA REPORT COMPLETO
                print("📊 Generazione report completo...")
                report_gen = ReportGenerator()
                report_paths = report_gen.generate_comprehensive_report(
                    risultati_screening, 
                    risultati_backtest
                )
    
                print(f"📄 Report generati:")
                print(f"  - Dashboard: {report_paths['html_dashboard']}")
                print(f"  - PDF: {report_paths['pdf_report']}")
    
                return risultati_backtest
        elif scelta == "3":
            print("📁 Caricamento screening precedente...")
            # Qui puoi aggiungere il caricamento da file JSON salvato
            print("⚠️  Funzionalità in sviluppo - usa opzione 2 per ora")
            
        else:
            print("❌ Scelta non valida")
            
    except Exception as e:
        print(f"❌ Errore backtesting: {e}")
        import traceback
        traceback.print_exc()
        
def test_struttura():
    """Testa la struttura del repository"""
    print("\n🧪 TEST STRUTTURA REPOSITORY")
    
    cartelle_necessarie = ['src', 'outputs', 'data', 'docs', 'outputs/screens', 'outputs/backtests', 'outputs/reports', 'outputs/archive']
    
    for cartella in cartelle_necessarie:
        if os.path.exists(cartella):
            print(f"✅ {cartella}/")
        else:
            print(f"❌ {cartella}/ (mancante)")
    
    print("\n📁 File principali:")
    file_necessari = ['src/mio_stock_finder.py', 'main_integrator.py']
    
    for file in file_necessari:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (mancante)")

if __name__ == "__main__":
    main()
