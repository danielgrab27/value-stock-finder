print("🎯 IL MIO VALUE STOCK FINDER AVANZATO!")
print("=" * 50)

import yfinance as yf
import pandas as pd
from datetime import datetime

# ==================== NUOVE FUNZIONI AGGIUNTE ====================

def check_quality_metrics(info):
    """Controlla la qualità aziendale per evitare value traps"""
    try:
        debito_lungo = info.get('longTermDebt', 0)
        cash_flow = info.get('operatingCashflow', 0)
        roe = info.get('returnOnEquity', 0)
        margini = info.get('profitMargins', 0)
        current_ratio = info.get('currentRatio', 0)
        
        punteggio = 0
        
        # 1. Debito gestibile (debito < 3x cash flow)
        if debito_lungo < cash_flow * 3 and debito_lungo > 0:
            punteggio += 1
        elif debito_lungo == 0:
            punteggio += 1  # Nessun debito è buono
            
        # 2. Cash flow positivo
        if cash_flow > 0:
            punteggio += 1
            
        # 3. ROE decente (>8%)
        if roe and roe > 0.08:
            punteggio += 1
            
        # 4. Margini di profitto positivi
        if margini and margini > 0.05:
            punteggio += 1
            
        # 5. Liquidità sana (current ratio > 1)
        if current_ratio and current_ratio > 1:
            punteggio += 1
            
        return punteggio >= 3  # Passa se almeno 3/5 criteri
        
    except:
        return False  # In caso di errore, meglio essere conservativi

def analisi_rischio(info):
    """Analizza il profilo di rischio dell'azienda"""
    punteggio_rischio = 0
    
    # Beta alto = più volatile
    beta = info.get('beta', 1)
    if beta > 1.5: 
        punteggio_rischio += 2
    elif beta > 1.2:
        punteggio_rischio += 1
        
    # Debito eccessivo
    debt_to_equity = info.get('debtToEquity', 0)
    if debt_to_equity > 2:
        punteggio_rischio += 2
    elif debt_to_equity > 1:
        punteggio_rischio += 1
        
    # Settore ad alto rischio
    sector = str(info.get('sector', '')).lower()
    settori_rischiosi = ['technology', 'healthcare', 'energy']
    if any(s in sector for s in settori_rischiosi):
        punteggio_rischio += 1
        
    # Classifica rischio
    if punteggio_rischio <= 1:
        return "Basso"
    elif punteggio_rischio <= 3:
        return "Medio"
    else:
        return "Alto"

def valuation_settoriale(info, eps, book_val):
    """Adatta la valuation in base al settore"""
    sector = str(info.get('sector', '')).lower()
    
    # Per tech/growth: considera la crescita
    if any(keyword in sector for keyword in ['technology', 'healthcare']):
        growth_rate = info.get('earningsGrowth', 0) or 0
        # Limita il premium di crescita per sicurezza
        growth_adjustment = 1 + min(growth_rate, 0.15)  
        valore_base = (22.5 * eps * book_val) ** 0.5
        return valore_base * growth_adjustment
    
    # Per finanziarie: focus su book value
    elif 'financial' in sector:
        # Usa P/B ratio più conservativo per le banche
        return book_val * 1.2  # Piccolo premium sul book value
    
    # Default: formula Graham tradizionale
    else:
        return (22.5 * eps * book_val) ** 0.5

# ==================== FUNZIONE PRINCIPALE MIGLIORATA ====================

def analizza_azione_avanzata(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        print(f"\n📊 {ticker}: {info.get('longName', 'N/A')[:30]}...")
        print(f"   🏭 Settore: {info.get('sector', 'N/A')}")
        print(f"   💰 Prezzo: ${info.get('currentPrice', 'N/A')}")
        print(f"   📈 P/E: {info.get('trailingPE', 'N/A')}")
        
        # CALCOLO VALORE INTRINSECO MIGLIORATO
        eps = info.get('trailingEps')
        book_val = info.get('bookValue')
        prezzo_attuale = info.get('currentPrice')
        
        if eps and book_val and eps > 0 and prezzo_attuale:
            # 🔥 NUOVO: Valuation settoriale invece di formula fissa
            valore_intrinseco = valuation_settoriale(info, eps, book_val)
            sconto = ((valore_intrinseco - prezzo_attuale) / valore_intrinseco) * 100
            
            # 🔥 NUOVO: Controllo qualità
            qualita_ok = check_quality_metrics(info)
            
            # 🔥 NUOVO: Analisi rischio
            rischio = analisi_rischio(info)
            
            print(f"   🎯 Valore Intrinseco: ${valore_intrinseco:.2f}")
            
            # 🔥 NUOVO: Output più informativo
            if sconto > 0 and qualita_ok:
                print(f"   🔥 SCONTO: {sconto:.1f}% | Qualità: ✅ | Rischio: {rischio} ✅")
            elif sconto > 0 and not qualita_ok:
                print(f"   ⚠️  SCONTO: {sconto:.1f}% | Qualità: ❌ | Attenzione: Value Trap!")
            else:
                print(f"   ⚠️  SOVRAPREZZO: {abs(sconto):.1f}%")
                
            return {
                'ticker': ticker,
                'nome': info.get('longName', ''),
                'settore': info.get('sector', ''),
                'prezzo': prezzo_attuale,
                'valore_intrinseco': valore_intrinseco,
                'sconto': sconto,
                'qualita_ok': qualita_ok,
                'rischio': rischio,
                'pe_ratio': info.get('trailingPE'),
                'roe': info.get('returnOnEquity'),
                'debito_equity': info.get('debtToEquity')
            }
        else:
            print(f"   ❌ Dati insufficienti per calcolo")
            return None
            
    except Exception as e:
        print(f"   ❌ Errore con {ticker}: {str(e)[:50]}...")
        return None

# ==================== ESECUZIONE MIGLIORATA ====================

# LISTA AZIONI DA ANALIZZARE (aggiunte alcune value stocks)
azioni = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'JNJ', 'JPM', 'XOM',
    'V', 'WMT', 'PG', 'KO', 'PEP', 'MCD', 'ABBV', 'AVGO', 'LLY', 'UNH',
    'HD', 'MA', 'BAC', 'CSCO', 'DIS', 'INTC', 'CRM', 'NFLX', 'ADBE', 'PYPL',
    'T', 'VZ', 'BMY', 'PFE', 'MRK']  # Aggiunte telecom e pharma

print(f"\n🔍 Analizzando {len(azioni)} azioni...")
print(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
print("-" * 50)

risultati = []
for azione in azioni:
    risultato = analizza_azione_avanzata(azione)
    if risultato:
        risultati.append(risultato)

# 🔥 NUOVO: MIGLIORI OPPORTUNITÀ FILTRATE
if risultati:
    print(f"\n🏆 MIGLIORI OPPORTUNITÀ (Sconti REALI con qualità):")
    print("-" * 50)
    
    # Filtra solo quelle con sconto E qualità OK
    opportunita_reali = [r for r in risultati if r['sconto'] > 0 and r['qualita_ok']]
    
    if opportunita_reali:
        risultati_ordinati = sorted(opportunita_reali, key=lambda x: x['sconto'], reverse=True)
        
        for i, risultato in enumerate(risultati_ordinati[:10], 1):  # Top 10
            emoji_rischio = "🟢" if risultato['rischio'] == "Basso" else "🟡" if risultato['rischio'] == "Medio" else "🔴"
            print(f"{i}. {risultato['ticker']}: {risultato['sconto']:.1f}% sconto")
            print(f"   💰 Prezzo: ${risultato['prezzo']:.2f} | Valore: ${risultato['valore_intrinseco']:.2f}")
            print(f"   ⚖️  Rischio: {risultato['rischio']} {emoji_rischio} | Settore: {risultato['settore']}")
    else:
        print("🤔 Nessuna opportunità di qualità trovata oggi")

# 🔥 NUOVO: VALUE TRAPS (sconti ma bassa qualità)
value_traps = [r for r in risultati if r['sconto'] > 0 and not r['qualita_ok']]
if value_traps:
    print(f"\n🚨 VALUE TRAPS (Sconti ma bassa qualità):")
    print("-" * 40)
    for trap in value_traps[:5]:
        print(f"⚠️  {trap['ticker']}: {trap['sconto']:.1f}% sconto | Problemi di qualità")

print("\n" + "=" * 50)
print("✅ ANALISI COMPLETATA!")
print(f"📊 Azioni analizzate: {len(azioni)}")
print(f"🎯 Opportunità di qualità: {len(opportunita_reali) if 'opportunita_reali' in locals() else 0}")
print(f"🚨 Value traps identificati: {len(value_traps)}")

# 🔥 NUOVO: SALVATAGGIO MIGLIORATO
if risultati:
    df = pd.DataFrame(risultati)
    
    # Aggiungi raccomandazione
    def raccomandazione(row):
        if row['sconto'] > 10 and row['qualita_ok'] and row['rischio'] == "Basso":
            return "FORTE ACQUISTO"
        elif row['sconto'] > 5 and row['qualita_ok']:
            return "ACQUISTA"
        elif row['sconto'] > 0 and not row['qualita_ok']:
            return "INVESTIGA"
        else:
            return "EVITA"
    
    df['raccomandazione'] = df.apply(raccomandazione, axis=1)
    
    # Salva
    data_oggi = datetime.now().strftime("%Y%m%d")
    nome_file = f"analisi_avanzata_{data_oggi}.csv"
    df.to_csv(nome_file, index=False)
    
    print(f"\n💾 Risultati salvati in '{nome_file}'")
    print(f"📊 Riepilogo raccomandazioni:")
    print(df['raccomandazione'].value_counts())

print("\n" + "=" * 50)
