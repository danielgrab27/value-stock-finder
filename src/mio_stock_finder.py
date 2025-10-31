print("🎯 IL MIO VALUE STOCK FINDER AVANZATO!")
print("=" * 50)

import yfinance as yf
import pandas as pd
from datetime import datetime
import time  # 🔥 NUOVO IMPORT per le pause

# ==================== CONFIGURAZIONE CENTRALIZZATA ====================

CONFIG = {
    'MIN_DISCOUNT': 5.0,           # Sconto minimo per considerare un'opportunità
    'MIN_QUALITY_SCORE': 3,        # Punteggio qualità minimo
    'MAX_RISK_LEVEL': 'Medio',     # Livello rischio massimo accettabile
    'SCORING_WEIGHTS': {
        'value': 0.5,              # Peso del valore (sconto)
        'quality': 0.3,            # Peso della qualità 
        'risk': 0.2                # Peso del rischio
    },
    'MIN_INVESTMENT_SCORE': 60,    # Punteggio minimo per "ACQUISTA"
    'PAUSE_EVERY': 10,             # 🔥 PAUSA ogni N azioni
    'PAUSE_SECONDS': 2             # 🔥 Secondi di pausa
}

def analizza_azioni_avanzata():
    """Versione che restituisce i risultati per l'integrazione"""
    print(f"\n🔍 Analizzando {len(azioni)} azioni...")
    print(f"⚙️  Configurazione: Sconto min {CONFIG['MIN_DISCOUNT']}% | Qualità min {CONFIG['MIN_QUALITY_SCORE']}/5")
    print(f"⏰ Pause: ogni {CONFIG['PAUSE_EVERY']} azioni per {CONFIG['PAUSE_SECONDS']} secondi")
    print(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("-" * 50)

    risultati = []
    for i, azione in enumerate(azioni):
        risultato = analizza_azione_avanzata(azione)
        if risultato:
            risultati.append(risultato)
        
        # 🔥 PAUSA PER EVITARE RATE LIMITING
        if (i + 1) % CONFIG['PAUSE_EVERY'] == 0 and (i + 1) < len(azioni):
            print(f"\n⏳ Pausa di {CONFIG['PAUSE_SECONDS']} secondi... ({i+1}/{len(azioni)} azioni completate)")
            time.sleep(CONFIG['PAUSE_SECONDS'])
    
    # 🔥 IMPORTANTE: RESTITUISCE I RISULTATI per l'integrazione
    return risultati

# ==================== GESTIONE ERRORI AVANZATA ====================

def safe_get(info, key, default=None):
    """Recupera valori safely da dizionari nidificati"""
    try:
        # Se la key è semplice, restituisci direttamente
        if '.' not in key:
            return info.get(key, default)
        
        # Se la key è nidificata (es: 'balanceSheet.quarterly.debt')
        keys = key.split('.')
        value = info
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, {})
            else:
                return default
        return value if value != {} else default
    except:
        return default

# ==================== CACHING PER PERFORMANCE ====================

stock_cache = {}

def get_cached_stock(ticker):
    """Ottiene i dati del ticker dalla cache o da Yahoo Finance"""
    if ticker not in stock_cache:
        stock_cache[ticker] = yf.Ticker(ticker)
    return stock_cache[ticker]

# ==================== SISTEMA DI SCORING ====================

def calculate_investment_score(analysis):
    """Calcola un punteggio di investimento 0-100"""
    # Punteggio Valore (max 50 punti)
    value_score = min(analysis['sconto'] * 2, 50)  # 1% sconto = 2 punti
    
    # Punteggio Qualità (max 30 punti)
    quality_score = 30 if analysis['qualita_ok'] else 0
    
    # Punteggio Rischio (max 20 punti)
    risk_scores = {'Basso': 20, 'Medio': 15, 'Alto': 5}
    risk_score = risk_scores.get(analysis['rischio'], 0)
    
    return value_score + quality_score + risk_score

def calculate_quality_score(info):
    """Calcola un punteggio di qualità più granulare 0-10"""
    score = 0
    
    # 1. Redditività (ROE)
    roe = safe_get(info, 'returnOnEquity', 0)
    if roe > 0.15: score += 2
    elif roe > 0.08: score += 1
    
    # 2. Margini di profitto
    margins = safe_get(info, 'profitMargins', 0)
    if margins > 0.15: score += 2
    elif margins > 0.08: score += 1
    
    # 3. Gestione debito
    debt_to_equity = safe_get(info, 'debtToEquity', 0)
    if debt_to_equity < 0.5: score += 2
    elif debt_to_equity < 1.0: score += 1
    
    # 4. Cash flow
    operating_cf = safe_get(info, 'operatingCashflow', 0)
    if operating_cf > 0: score += 2
    
    # 5. Liquidità
    current_ratio = safe_get(info, 'currentRatio', 0)
    if current_ratio > 1.5: score += 2
    elif current_ratio > 1.0: score += 1
    
    return score

def get_stelle_rating(score):
    """Converte il punteggio in stelle, gestendo qualsiasi tipo di numero"""
    try:
        score_int = int(float(score))  # Converti prima in float poi in int
        return "★" * (score_int // 20)
    except:
        return ""  # Se c'è errore, restituisci stringa vuota

# ==================== FUNZIONI ESISTENTI MIGLIORATE ====================

def check_quality_metrics(info):
    """Controlla la qualità aziendale per evitare value traps - VERSIONE MIGLIORATA"""
    try:
        # Usa safe_get invece di .get() diretto
        debito_lungo = safe_get(info, 'longTermDebt', 0)
        cash_flow = safe_get(info, 'operatingCashflow', 0)
        roe = safe_get(info, 'returnOnEquity', 0)
        margini = safe_get(info, 'profitMargins', 0)
        current_ratio = safe_get(info, 'currentRatio', 0)
        
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
            
        return punteggio >= CONFIG['MIN_QUALITY_SCORE']  # Usa la configurazione
        
    except:
        return False

def analisi_rischio(info):
    """Analizza il profilo di rischio dell'azienda - VERSIONE MIGLIORATA"""
    punteggio_rischio = 0
    
    # Beta alto = più volatile
    beta = safe_get(info, 'beta', 1)
    if beta > 1.5: 
        punteggio_rischio += 2
    elif beta > 1.2:
        punteggio_rischio += 1
        
    # Debito eccessivo
    debt_to_equity = safe_get(info, 'debtToEquity', 0)
    if debt_to_equity > 2:
        punteggio_rischio += 2
    elif debt_to_equity > 1:
        punteggio_rischio += 1
        
    # Settore ad alto rischio
    sector = str(safe_get(info, 'sector', '')).lower()
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
    """Adatta la valuation in base al settore - VERSIONE MIGLIORATA"""
    sector = str(safe_get(info, 'sector', '')).lower()
    
    # Per tech/growth: considera la crescita
    if any(keyword in sector for keyword in ['technology', 'healthcare']):
        growth_rate = safe_get(info, 'earningsGrowth', 0) or 0
        # Limita il premium di crescita per sicurezza
        growth_adjustment = 1 + min(growth_rate, 0.15)  
        valore_base = (22.5 * eps * book_val) ** 0.5
        return valore_base * growth_adjustment
    
    # Per finanziarie: focus su book value
    elif 'financial' in sector:
        # Usa P/B ratio più conservativo per le banche
        return book_val * 1.2
    
    # Default: formula Graham tradizionale
    else:
        return (22.5 * eps * book_val) ** 0.5

# ==================== FUNZIONE PRINCIPALE MIGLIORATA ====================

def analizza_azione_avanzata(ticker):
    try:
        # 🔥 USA CACHING invece di yf.Ticker() diretto
        stock = get_cached_stock(ticker)
        info = stock.info
        
        print(f"\n📊 {ticker}: {safe_get(info, 'longName', 'N/A')[:30]}...")
        print(f"   🏭 Settore: {safe_get(info, 'sector', 'N/A')}")
        print(f"   💰 Prezzo: ${safe_get(info, 'currentPrice', 'N/A')}")
        print(f"   📈 P/E: {safe_get(info, 'trailingPE', 'N/A')}")
        
        # CALCOLO VALORE INTRINSECO MIGLIORATO
        # 🔥 USA safe_get invece di .get()
        eps = safe_get(info, 'trailingEps')
        book_val = safe_get(info, 'bookValue')
        prezzo_attuale = safe_get(info, 'currentPrice')
        
        if eps and book_val and eps > 0 and prezzo_attuale:
            # Valuation settoriale invece di formula fissa
            valore_intrinseco = valuation_settoriale(info, eps, book_val)
            sconto = ((valore_intrinseco - prezzo_attuale) / valore_intrinseco) * 100
            
            # Controllo qualità
            qualita_ok = check_quality_metrics(info)
            
            # Analisi rischio
            rischio = analisi_rischio(info)
            
            # 🔥 NUOVO: Calcolo punteggio investimento
            investment_score = calculate_investment_score({
                'sconto': sconto,
                'qualita_ok': qualita_ok,
                'rischio': rischio
            })
            
            # 🔥 NUOVO: Calcolo punteggio qualità dettagliato
            quality_score_detailed = calculate_quality_score(info)
            
            print(f"   🎯 Valore Intrinseco: ${valore_intrinseco:.2f}")
            print(f"   📊 Punteggio Investimento: {investment_score:.0f}/100")
            print(f"   🏅 Qualità Dettagliata: {quality_score_detailed}/10")
            
            # 🔥 NUOVO: Output più informativo con punteggio
            if sconto > 0 and qualita_ok:
                if investment_score >= 80:
                    print(f"   🔥 SCONTO: {sconto:.1f}% | Punteggio: {investment_score:.0f} | QUALITÀ ECCELLENTE! 🚀")
                else:
                    print(f"   🔥 SCONTO: {sconto:.1f}% | Punteggio: {investment_score:.0f} | Qualità: ✅ | Rischio: {rischio}")
            elif sconto > 0 and not qualita_ok:
                print(f"   ⚠️  SCONTO: {sconto:.1f}% | Punteggio: {investment_score:.0f} | Qualità: ❌ | Value Trap!")
            else:
                print(f"   ⚠️  SOVRAPREZZO: {abs(sconto):.1f}% | Punteggio: {investment_score:.0f}")
                
            return {
                'ticker': ticker,
                'nome': safe_get(info, 'longName', ''),
                'settore': safe_get(info, 'sector', ''),
                'prezzo': prezzo_attuale,
                'valore_intrinseco': valore_intrinseco,
                'sconto': sconto,
                'qualita_ok': qualita_ok,
                'rischio': rischio,
                'investment_score': investment_score,
                'quality_score_detailed': quality_score_detailed,
                'pe_ratio': safe_get(info, 'trailingPE'),
                'roe': safe_get(info, 'returnOnEquity'),
                'debito_equity': safe_get(info, 'debtToEquity')
            }
        else:
            print(f"   ❌ Dati insufficienti per calcolo")
            return None
            
    except Exception as e:
        print(f"   ❌ Errore con {ticker}: {str(e)[:50]}...")
        return None

# ==================== LISTA AZIONI COMPLETA (160+) ====================

azioni = [
    # 🔷 TECNOLOGIA (25)
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'AVGO', 'ADBE', 'CRM',
    'CSCO', 'INTC', 'ORCL', 'IBM', 'QCOM', 'TXN', 'AMD', 'NOW', 'UBER', 'SHOP',
    'NET', 'SNOW', 'PANW', 'CRWD', 'MSI',
    
    # 🏦 FINANZIARIE (20)
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'SCHW', 'BLK', 'C', 'AXP', 'V',
    'MA', 'PYPL', 'SQ', 'COF', 'DFS', 'RY', 'TD', 'BX', 'KKR', 'SPGI',
    
    # 🏥 HEALTHCARE (20)
    'JNJ', 'UNH', 'LLY', 'PFE', 'ABBV', 'TMO', 'MRK', 'DHR', 'AMGN', 'GILD',
    'BMY', 'VRTX', 'REGN', 'ISRG', 'SYK', 'BDX', 'ZTS', 'CI', 'HUM', 'EW',
    
    # 🏠 CONSUMO CICLICO (15)
    'HD', 'MCD', 'SBUX', 'NKE', 'LOW', 'TSCO', 'F', 'GM', 'MAR', 'HLT',
    'BKNG', 'NCLH', 'RCL', 'CCL', 'DHI',
    
    # 🛒 CONSUMO DIFENSIVO (15)
    'WMT', 'PG', 'KO', 'PEP', 'COST', 'PM', 'MO', 'MDLZ', 'CL', 'EL',
    'KMB', 'SYY', 'KR', 'TGT', 'DG',
    
    # ⚡ ENERGY & UTILITIES (15)
    'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX', 'VLO', 'MPC', 'OXY', 'KMI',
    'NEE', 'DUK', 'SO', 'D', 'AEP',
    
    # 🏭 INDUSTRIALI (15)
    'RTX', 'BA', 'LMT', 'GD', 'NOC', 'CAT', 'DE', 'HON', 'GE', 'UPS',
    'FDX', 'EMR', 'ITW', 'WM', 'RSG',
    
    # 🏢 MATERIALI & REAL ESTATE (15)
    'LIN', 'APD', 'FCX', 'NEM', 'GOLD', 'VALE', 'BHP', 'RIO', 'PLD', 'AMT',
    'CCI', 'EQIX', 'PSA', 'O', 'SPG',
    
    # 📱 TELECOM & MEDIA (15)
    'T', 'VZ', 'CMCSA', 'DIS', 'NFLX', 'CHTR', 'TMUS', 'EA', 'ATVI', 'TTWO',
    'LYV', 'LVS', 'WYNN', 'MGM', 'ROKU',
    
    # 🌍 INTERNAZIONALI (15)
    'ASML', 'NSRGY', 'SAP', 'UL', 'BUD', 'AZN', 'GSK', 'SNY', 'SAN', 'BBVA',
    'ING', 'HSBC', 'TM', 'HMC', 'SONY'
]

# ==================== CODICE ESECUZIONE DIRECTTA ====================

if __name__ == "__main__":
    # Quando eseguito direttamente, mostra output completo
    risultati = analizza_azioni_avanzata()
    
    # 🔥 NUOVO: MIGLIORI OPPORTUNITÀ CON PUNTEGGIO
    if risultati:
        print(f"\n🏆 MIGLIORI OPPORTUNITÀ (ordinate per punteggio):")
        print("-" * 50)
        
        # Filtra solo quelle con sconto E qualità OK
        opportunita_reali = [r for r in risultati if r['sconto'] > CONFIG['MIN_DISCOUNT'] and r['qualita_ok']]
        
        if opportunita_reali:
            # 🔥 ORDINA PER PUNTEGGIO invece che solo per sconto
            risultati_ordinati = sorted(opportunita_reali, key=lambda x: x['investment_score'], reverse=True)
            
            for i, risultato in enumerate(risultati_ordinati[:15], 1):  # Top 15 invece di 10
                emoji_rischio = "🟢" if risultato['rischio'] == "Basso" else "🟡" if risultato['rischio'] == "Medio" else "🔴"
                stelle = get_stelle_rating(risultato['investment_score'])
                
                print(f"{i}. {risultato['ticker']}: {risultato['sconto']:.1f}% sconto")
                print(f"   💰 Prezzo: ${risultato['prezzo']:.2f} | Valore: ${risultato['valore_intrinseco']:.2f}")
                print(f"   📊 Punteggio: {risultato['investment_score']:.0f}/100 {stelle}")
                print(f"   ⚖️  Rischio: {risultato['rischio']} {emoji_rischio} | Qualità: {risultato['quality_score_detailed']}/10")
        else:
            print("🤔 Nessuna opportunità di qualità trovata oggi")

    # VALUE TRAPS (sconti ma bassa qualità)
    value_traps = [r for r in risultati if r['sconto'] > 0 and not r['qualita_ok']]
    if value_traps:
        print(f"\n🚨 VALUE TRAPS (Sconti ma bassa qualità):")
        print("-" * 40)
        for trap in value_traps[:8]:  # Mostra più value traps
            print(f"⚠️  {trap['ticker']}: {trap['sconto']:.1f}% sconto | Qualità: {trap['quality_score_detailed']}/10")

    print("\n" + "=" * 50)
    print("✅ ANALISI COMPLETATA!")
    print(f"📊 Azioni analizzate: {len(azioni)}")
    print(f"🎯 Opportunità di qualità: {len(opportunita_reali)}")
    print(f"🚨 Value traps identificati: {len(value_traps)}")

    # 🔥 NUOVO: SALVATAGGIO MIGLIORATO CON PUNTEGGI
    if risultati:
        df = pd.DataFrame(risultati)
        
        # Aggiungi raccomandazione basata su punteggio
        def raccomandazione(row):
            if row['investment_score'] >= 80:
                return "FORTE ACQUISTO 🚀"
            elif row['investment_score'] >= 60:
                return "ACQUISTA ✅"
            elif row['sconto'] > 0 and not row['qualita_ok']:
                return "INVESTIGA 🔍"
            else:
                return "EVITA ❌"
        
        df['raccomandazione'] = df.apply(raccomandazione, axis=1)
        
        # Ordina per punteggio prima di salvare
        df = df.sort_values('investment_score', ascending=False)
        
        # Salva
        data_oggi = datetime.now().strftime("%Y%m%d_%H%M")
        nome_file = f"analisi_avanzata_{data_oggi}.csv"
        df.to_csv(nome_file, index=False)
        
        print(f"\n💾 Risultati salvati in '{nome_file}'")
        
        # 🔥 OUTPUT PIÙ PULITO senza "Name: count, dtype: int64"
        print(f"📊 Riepilogo raccomandazioni:")
        conteggi = df['raccomandazione'].value_counts()
        for raccomandazione, count in conteggi.items():
            print(f"   {raccomandazione}: {count} azioni")

    print("\n" + "=" * 50)
