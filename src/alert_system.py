"""
🚨 ALERT SYSTEM - Value Stock Finder
Sistema di notifiche per opportunità eccezionali e value traps pericolosi
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class AlertSystem:
    def __init__(self, config: Dict = None):
        self.config = config or {
            'EXCEPTIONAL_OPPORTUNITY_SCORE': 90,
            'HIGH_RISK_VALUE_TRAP_SCORE': 30,
            'MIN_DISCOUNT_EXCEPTIONAL': 25.0,
            'MAX_RISK_EXCEPTIONAL': 'Medio',
            'ENABLE_HISTORICAL_ALERTS': True
        }
        
        self.alert_history = []
        self.output_dir = "outputs/alerts"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def analyze_opportunities(self, screening_results: List[Dict]) -> Dict[str, List]:
        """
        Analizza i risultati dello screening e genera alert
        """
        exceptional_opportunities = []
        high_risk_traps = []
        quality_opportunities = []
        
        for stock in screening_results:
            # Opportunità Eccezionali
            if self._is_exceptional_opportunity(stock):
                exceptional_opportunities.append(stock)
            
            # Value Traps Pericolosi
            elif self._is_high_risk_trap(stock):
                high_risk_traps.append(stock)
            
            # Opportunità di Qualità (per reporting)
            elif self._is_quality_opportunity(stock):
                quality_opportunities.append(stock)
        
        return {
            'exceptional': exceptional_opportunities,
            'high_risk_traps': high_risk_traps,
            'quality': quality_opportunities
        }
    
    def _is_exceptional_opportunity(self, stock: Dict) -> bool:
        """Determina se un'azione è un'opportunità eccezionale"""
        try:
            score = stock.get('investment_score', 0)
            discount = stock.get('sconto', 0)
            risk = stock.get('rischio', 'Alto')
            quality_ok = stock.get('qualita_ok', False)
            
            return (score >= self.config['EXCEPTIONAL_OPPORTUNITY_SCORE'] and
                    discount >= self.config['MIN_DISCOUNT_EXCEPTIONAL'] and
                    risk in ['Basso', 'Medio'] and
                    quality_ok)
        except:
            return False
    
    def _is_high_risk_trap(self, stock: Dict) -> bool:
        """Identifica value traps ad alto rischio"""
        try:
            score = stock.get('investment_score', 0)
            discount = stock.get('sconto', 0)
            risk = stock.get('rischio', 'Alto')
            quality_ok = stock.get('qualita_ok', False)
            quality_score = stock.get('quality_score_detailed', 0)
            
            # Value trap: alto sconto ma bassa qualità e alto rischio
            return (discount > 15.0 and 
                    not quality_ok and 
                    risk == 'Alto' and 
                    quality_score <= 3 and
                    score <= self.config['HIGH_RISK_VALUE_TRAP_SCORE'])
        except:
            return False
    
    def _is_quality_opportunity(self, stock: Dict) -> bool:
        """Identifica opportunità di qualità standard"""
        try:
            score = stock.get('investment_score', 0)
            discount = stock.get('sconto', 0)
            quality_ok = stock.get('qualita_ok', False)
            
            return (score >= 70 and discount >= 10.0 and quality_ok)
        except:
            return False
    
    def generate_alerts(self, analysis_results: Dict) -> None:
        """
        Genera e mostra gli alert nel sistema
        """
        exceptional = analysis_results['exceptional']
        traps = analysis_results['high_risk_traps']
        quality = analysis_results['quality']
        
        self._show_alert_header()
        
        # Alert Opportunità Eccezionali
        if exceptional:
            self._show_exceptional_alerts(exceptional)
        else:
            print("   ✅ Nessuna opportunità eccezionale rilevata")
        
        # Alert Value Traps
        if traps:
            self._show_trap_alerts(traps)
        else:
            print("   ✅ Nessun value trap pericoloso rilevato")
        
        # Riepilogo Qualità
        self._show_quality_summary(quality)
        
        # Salva storico
        if self.config['ENABLE_HISTORICAL_ALERTS']:
            self._save_alert_history(analysis_results)
    
    def _show_alert_header(self):
        """Mostra l'header del sistema di alert"""
        print("\n" + "🚨" * 20)
        print("🚨          SISTEMA DI ALERT - VALUE STOCK FINDER          🚨")
        print("🚨" * 20)
        print(f"📅 Data analisi: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"⚙️  Soglie: Score >{self.config['EXCEPTIONAL_OPPORTUNITY_SCORE']} | Sconto >{self.config['MIN_DISCOUNT_EXCEPTIONAL']}%")
        print("-" * 60)
    
    def _show_exceptional_alerts(self, opportunities: List[Dict]):
        """Mostra alert per opportunità eccezionali"""
        print(f"\n🎯 OPPORTUNITÀ ECCEZIONALI TROVATE: {len(opportunities)}")
        print("=" * 50)
        
        for i, opp in enumerate(opportunities, 1):
            print(f"{i}. 🔥 {opp['ticker']} - {opp.get('nome', '')[:25]}...")
            print(f"   💎 Score: {opp['investment_score']:.0f}/100 | Sconto: {opp['sconto']:.1f}%")
            print(f"   💰 Prezzo: ${opp['prezzo']:.2f} | Valore: ${opp['valore_intrinseco']:.2f}")
            print(f"   ⚖️  Rischio: {opp['rischio']} | Qualità: {opp['quality_score_detailed']}/10")
            print(f"   🏭 Settore: {opp.get('settore', 'N/A')}")
            print(f"   📈 P/E: {opp.get('pe_ratio', 'N/A')} | ROE: {opp.get('roe', 'N/A')}")
            print("   " + "─" * 40)
    
    def _show_trap_alerts(self, traps: List[Dict]):
        """Mostra alert per value traps pericolosi"""
        print(f"\n⚠️  VALUE TRAPS PERICOLOSI: {len(traps)}")
        print("=" * 45)
        
        for i, trap in enumerate(traps, 1):
            print(f"{i}. 🚨 {trap['ticker']} - {trap.get('nome', '')[:20]}...")
            print(f"   💀 Score: {trap['investment_score']:.0f}/100 | Sconto: {trap['sconto']:.1f}%")
            print(f"   ❌ Qualità: {trap['quality_score_detailed']}/10 | Rischio: {trap['rischio']}")
            print(f"   📉 P/E: {trap.get('pe_ratio', 'N/A')} | Debito/Equity: {trap.get('debito_equity', 'N/A')}")
            print("   " + "─" * 40)
    
    def _show_quality_summary(self, quality_opps: List[Dict]):
        """Mostra riepilogo opportunità di qualità"""
        if quality_opps:
            print(f"\n📊 OPPORTUNITÀ DI QUALITÀ: {len(quality_opps)}")
            print("=" * 40)
            
            # Top 5 per score
            top_5 = sorted(quality_opps, key=lambda x: x['investment_score'], reverse=True)[:5]
            
            for i, opp in enumerate(top_5, 1):
                print(f"{i}. {opp['ticker']}: Score {opp['investment_score']:.0f} | Sconto {opp['sconto']:.1f}%")
    
    def _save_alert_history(self, analysis_results: Dict):
        """Salva lo storico degli alert"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'exceptional_count': len(analysis_results['exceptional']),
            'trap_count': len(analysis_results['high_risk_traps']),
            'quality_count': len(analysis_results['quality']),
            'exceptional_opportunities': [
                {
                    'ticker': opp['ticker'],
                    'score': opp['investment_score'],
                    'discount': opp['sconto'],
                    'price': opp['prezzo'],
                    'risk': opp['rischio']
                } for opp in analysis_results['exceptional']
            ],
            'high_risk_traps': [
                {
                    'ticker': trap['ticker'],
                    'score': trap['investment_score'],
                    'discount': trap['sconto'],
                    'risk': trap['rischio']
                } for trap in analysis_results['high_risk_traps']
            ]
        }
        
        filename = os.path.join(self.output_dir, f"alerts_{timestamp}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(alert_data, f, indent=2, ensure_ascii=False)
        
        # Aggiorna storico in memoria
        self.alert_history.append(alert_data)
        
        print(f"\n💾 Storico alert salvato in: {filename}")

# Singleton per uso globale
_alert_system_instance = None

def get_alert_system(config: Dict = None) -> AlertSystem:
    """Restituisce l'istanza singleton del sistema di alert"""
    global _alert_system_instance
    if _alert_system_instance is None:
        _alert_system_instance = AlertSystem(config)
    return _alert_system_instance
