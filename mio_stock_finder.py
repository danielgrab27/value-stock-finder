print("🎯 IL MIO VALUE STOCK FINDER!")
print("=" * 45)

import yfinance as yf
import pandas as pd
from datetime import datetime

def analizza_azione(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        print(f"\n📊 {ticker}:")
        print(f"   💰 Prezzo: ${info.get('currentPrice', 'N/A')}")
        print(f"   📈 P/E Ratio: {info.get('trailingPE', 'N/A')}")
        print(f"   🏦 Book Value: ${info.get('bookValue', 'N/A')}")
        print(f"   💵 EPS: ${info.get('trailingEps', 'N/A')}")
        
        # CALCOLO VALORE INTRINSECO
        eps = info.get('trailingEps')
        book_val = info.get('bookValue')
        prezzo_attuale = info.get('currentPrice')
        
        if eps and book_val and eps > 0 and prezzo_attuale:
            # Formula di Benjamin Graham
            valore_graham = (22.5 * eps * book_val) ** 0.5
            sconto = ((valore_graham - prezzo_attuale) / valore_graham) * 100
            
            print(f"   🎯 Valore Graham: ${valore_graham:.2f}")
            
            if sconto > 0:
                print(f"   🔥 SCONTO: {sconto:.1f}% ✅")
            else:
                print(f"   ⚠️  SOVRAPREZZO: {abs(sconto):.1f}%")
                
            return {
                'ticker': ticker,
                'prezzo': prezzo_attuale,
                'valore_graham': valore_graham,
                'sconto': sconto
            }
        else:
            print(f"   ❌ Dati insufficienti per calcolo")
            return None
            
    except Exception as e:
        print(f"   ❌ Errore con {ticker}: {str(e)[:50]}...")
        return None

# LISTA AZIONI DA ANALIZZARE
azioni = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'JNJ', 'JPM', 'XOM',
    'V', 'WMT', 'PG', 'KO', 'PEP', 'MCD', 'ABBV', 'AVGO', 'LLY', 'UNH',
    'HD', 'MA', 'BAC', 'CSCO', 'DIS', 'INTC', 'CRM', 'NFLX', 'ADBE', 'PYPL']

print(f"\n🔍 Analizzando {len(azioni)} azioni...")
print(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
print("-" * 45)

risultati = []
for azione in azioni:
    risultato = analizza_azione(azione)
    if risultato:
        risultati.append(risultato)

# MOSTRA MIGLIORI OPPORTUNITÀ
if risultati:
    print(f"\n🏆 MIGLIORI OPPORTUNITÀ (ordinate per sconto):")
    print("-" * 45)
    
    risultati_ordinati = sorted(risultati, key=lambda x: x['sconto'], reverse=True)
    
    for i, risultato in enumerate(risultati_ordinati[:5], 1):
        if risultato['sconto'] > 0:
            print(f"{i}. {risultato['ticker']}: {risultato['sconto']:.1f}% sconto")
            print(f"   Prezzo: ${risultato['prezzo']} | Valore: ${risultato['valore_graham']:.2f}")

print("\n" + "=" * 45)
print("✅ ANALISI COMPLETATA!")
print(f"📊 Azioni analizzate: {len(azioni)}")
print(f"🎯 Opportunità trovate: {len([r for r in risultati if r['sconto'] > 0])}")

# Salva risultati in CSV
if risultati:
    # Crea un DataFrame (tabella) con i risultati
    df = pd.DataFrame(risultati)
    
    # Aggiungi data all'filename
    from datetime import datetime
    data_oggi = datetime.now().strftime("%Y%m%d")
    nome_file = f"risultati_analisi_{data_oggi}.csv"
    
    # Salva il file
    df.to_csv(nome_file, index=False)
    print(f"💾 Risultati salvati in '{nome_file}'")
    
    # Mostra anteprima
    print(f"📄 Prime 30 righe salvate:")
    print(df.head(30))
else:
    print("❌ Nessun risultato da salvare")

print("\n" + "=" * 50)

