"""
🧪 TEST ALERT SYSTEM
"""

import sys
import os
sys.path.append('src')

from alert_system import AlertSystem

def test_alert_system():
    """Test del sistema di alert con dati di esempio"""
    print("🧪 TEST SISTEMA DI ALERT")
    print("=" * 40)
    
    # Crea sistema di alert
    alert_system = AlertSystem()
    
    # Dati di test
    test_data = [
        {
            'ticker': 'TEST1',
            'nome': 'Test Company Eccezionale',
            'investment_score': 95,
            'sconto': 30.5,
            'prezzo': 50.0,
            'valore_intrinseco': 75.0,
            'qualita_ok': True,
            'rischio': 'Medio',
            'quality_score_detailed': 8,
            'settore': 'Technology',
            'pe_ratio': 12.5,
            'roe': 0.15
        },
        {
            'ticker': 'TEST2',
            'nome': 'Test Value Trap',
            'investment_score': 25,
            'sconto': 18.0,
            'prezzo': 20.0,
            'valore_intrinseco': 25.0,
            'qualita_ok': False,
            'rischio': 'Alto',
            'quality_score_detailed': 2,
            'settore': 'Energy',
            'pe_ratio': 45.0,
            'debito_equity': 3.5
        },
        {
            'ticker': 'TEST3',
            'nome': 'Test Qualità Normale',
            'investment_score': 75,
            'sconto': 12.0,
            'prezzo': 80.0,
            'valore_intrinseco': 90.0,
            'qualita_ok': True,
            'rischio': 'Basso',
            'quality_score_detailed': 7,
            'settore': 'Healthcare'
        }
    ]
    
    # Analizza opportunità
    results = alert_system.analyze_opportunities(test_data)
    
    # Genera alert
    alert_system.generate_alerts(results)
    
    print("\n✅ Test completato!")

if __name__ == "__main__":
    test_alert_system()
