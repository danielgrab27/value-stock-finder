"""
📊 BACKTESTING MODULE - Value Stock Finder
Analizza performance storica delle strategie value
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json

def analizza_performance_storica(ticker, anni=3):
    """
    Analizza la performance storica di un'azione
    """
    try:
        print(f"📈 Analisi storica {ticker} ({anni} anni)...")
        
        # Calcola date
        end_date = datetime.now()
        start_date = end_date - timedelta(days=anni*365)
        
        # Download dati storici
        stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if stock_data.empty or len(stock_data) < 30:
            return None
        
        # Calcola metriche performance
        prezzo_iniziale = stock_data['Close'].iloc[0]
        prezzo_attuale = stock_data['Close'].iloc[-1]
        rendimento_totale = ((prezzo_attuale - prezzo_iniziale) / prezzo_iniziale) * 100
        
        # Volatilità (deviazione standard rendimenti giornalieri)
        rendimenti_giornalieri = stock_data['Close'].pct_change().dropna()
        volatilita = rendimenti_giornalieri.std() * 100
        
        # Massimo drawdown
        rolling_max = stock_data['Close'].expanding().max()
        drawdown = (stock_data['Close'] - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()
        
        return {
            'ticker': ticker,
            'periodo_analisi_anni': anni,
            'prezzo_iniziale': round(prezzo_iniziale, 2),
            'prezzo_attuale': round(prezzo_attuale, 2),
            'rendimento_totale_perc': round(rendimento_totale, 2),
            'volatilita_annualizzata': round(volatilita, 2),
            'max_drawdown_perc': round(max_drawdown, 2),
            'sharpe_ratio': round(rendimento_totale / volatilita, 2) if volatilita > 0 else 0,
            'data_inizio': start_date.strftime('%Y-%m-%d'),
            'data_fine': end_date.strftime('%Y-%m-%d')
        }
        
    except Exception as e:
        print(f"❌ Errore analisi storica {ticker}: {e}")
        return None

def backtest_opportunita(opportunita, anni=3):
    """
    Riceve le opportunità dallo screener e fa backtesting
    """
    print(f"\n🎯 BACKTESTING {len(opportunita)} OPPORTUNITÀ ({anni} anni)")
    print("=" * 50)
    
    risultati = []
    
    for opp in opportunita[:10]:  # Prime 10 opportunità per test
        ticker = opp['ticker']
        risultato_backtest = analizza_performance_storica(ticker, anni)
        
        if risultato_backtest:
            # Combina dati screening + backtesting
            risultato_combinato = {
                **opp,  # Dati dallo screening
                **risultato_backtest  # Dati dal backtesting
            }
            risultati.append(risultato_combinato)
            
            # Output progressivo
            rendimento = risultato_backtest['rendimento_totale_perc']
            drawdown = risultato_backtest['max_drawdown_perc']
            print(f"✅ {ticker}: {rendimento:>6.1f}% | Max Drawdown: {drawdown:>5.1f}%")
    
    return risultati

def salva_risultati_backtest(risultati, filename=None):
    """Salva i risultati del backtesting"""
    if not filename:
        data_oggi = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"outputs/backtests/backtest_{data_oggi}.json"
    
    with open(filename, 'w') as f:
        json.dump(risultati, f, indent=2)
    
    print(f"💾 Risultati backtest salvati in: {filename}")
    return filename

def test_backtest_sistema():
    """Test completo del sistema di backtesting"""
    print("🧪 TEST SISTEMA BACKTESTING")
    print("=" * 30)
    
    # Simula opportunità come le troverebbe lo screener
    opportunita_test = [
        {'ticker': 'AAPL', 'sconto': 15.5, 'investment_score': 85, 'rischio': 'Basso'},
        {'ticker': 'MSFT', 'sconto': 12.2, 'investment_score': 78, 'rischio': 'Basso'},
        {'ticker': 'JNJ', 'sconto': 8.7, 'investment_score': 72, 'rischio': 'Basso'},
        {'ticker': 'JPM', 'sconto': 5.3, 'investment_score': 65, 'rischio': 'Medio'}
    ]
    
    risultati = backtest_opportunita(opportunita_test, anni=3)
    print(f"\n📊 Backtesting completato: {len(risultati)} azioni analizzate")
    
    if risultati:
        salva_risultati_backtest(risultati)
    
    return risultati

if __name__ == "__main__":
    test_backtest_sistema()
