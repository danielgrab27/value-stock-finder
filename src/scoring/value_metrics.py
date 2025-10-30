import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from app.models.fundamentals import Fundamentals

@dataclass
class ValueScore:
    total_score: float
    component_scores: Dict[str, float]
    warnings: List[str]
    strengths: List[str]

class EnhancedValueScorer:
    def __init__(self):
        self.metrics_weights = {
            'pe_ratio': 0.15,
            'price_to_book': 0.15,
            'price_to_sales': 0.10,
            'ev_to_ebitda': 0.15,
            'dividend_yield': 0.10,
            'debt_to_equity': 0.10,
            'return_on_equity': 0.10,
            'earnings_growth': 0.10,
            'free_cash_flow_yield': 0.05
        }
        
    def calculate_score(self, fundamentals: Fundamentals, sector: str = None) -> ValueScore:
        """Calcola uno score di valore migliorato con analisi settoriale"""
        scores = {}
        warnings = []
        strengths = []
        
        # P/E Ratio Score
        if fundamentals.pe_ratio and fundamentals.pe_ratio > 0:
            if fundamentals.pe_ratio < 15:
                scores['pe_ratio'] = 100
                strengths.append("P/E ratio molto basso")
            elif fundamentals.pe_ratio < 25:
                scores['pe_ratio'] = 70
            elif fundamentals.pe_ratio < 35:
                scores['pe_ratio'] = 40
            else:
                scores['pe_ratio'] = 10
                warnings.append("P/E ratio elevato")
        else:
            scores['pe_ratio'] = 0
            warnings.append("P/E ratio non disponibile")
        
        # Price to Book Score
        if fundamentals.price_to_book_ratio:
            if fundamentals.price_to_book_ratio < 1:
                scores['price_to_book'] = 100
                strengths.append("Prezzo sotto il valore contabile")
            elif fundamentals.price_to_book_ratio < 1.5:
                scores['price_to_book'] = 80
            elif fundamentals.price_to_book_ratio < 2.5:
                scores['price_to_book'] = 50
            else:
                scores['price_to_book'] = 20
        else:
            scores['price_to_book'] = 0
        
        # EV/EBITDA Score
        if fundamentals.ev_to_ebitda:
            if fundamentals.ev_to_ebitda < 8:
                scores['ev_to_ebitda'] = 100
                strengths.append("EV/EBITDA molto favorevole")
            elif fundamentals.ev_to_ebitda < 12:
                scores['ev_to_ebitda'] = 75
            elif fundamentals.ev_to_ebitda < 15:
                scores['ev_to_ebitda'] = 50
            else:
                scores['ev_to_ebitda'] = 25
        else:
            scores['ev_to_ebitda'] = 0
        
        # Debt to Equity Score
        if fundamentals.debt_to_equity:
            if fundamentals.debt_to_equity < 0.5:
                scores['debt_to_equity'] = 100
                strengths.append("Basso livello di debito")
            elif fundamentals.debt_to_equity < 1.0:
                scores['debt_to_equity'] = 75
            elif fundamentals.debt_to_equity < 1.5:
                scores['debt_to_equity'] = 50
            else:
                scores['debt_to_equity'] = 25
                warnings.append("Livello di debito elevato")
        else:
            scores['debt_to_equity'] = 50  # Valore neutro se non disponibile
        
        # Return on Equity Score
        if fundamentals.return_on_equity:
            if fundamentals.return_on_equity > 0.15:
                scores['return_on_equity'] = 100
                strengths.append("Alto ritorno sul capitale")
            elif fundamentals.return_on_equity > 0.10:
                scores['return_on_equity'] = 80
            elif fundamentals.return_on_equity > 0.05:
                scores['return_on_equity'] = 60
            else:
                scores['return_on_equity'] = 30
        else:
            scores['return_on_equity'] = 0
        
        # Calcolo score totale ponderato
        total_score = sum(
            scores.get(metric, 0) * weight 
            for metric, weight in self.metrics_weights.items()
        )
        
        return ValueScore(
            total_score=total_score,
            component_scores=scores,
            warnings=warnings,
            strengths=strengths
        )
    
    def get_sector_adjusted_thresholds(self, sector: str) -> Dict[str, float]:
        """Restituisce le soglie adattate per il settore"""
        # Soglie specifiche per settore
        sector_thresholds = {
            'technology': {'pe_max': 30, 'pb_max': 3.0},
            'financial': {'pe_max': 15, 'pb_max': 1.2},
            'healthcare': {'pe_max': 25, 'pb_max': 2.5},
            'industrial': {'pe_max': 20, 'pb_max': 1.8},
            'consumer': {'pe_max': 22, 'pb_max': 2.0},
            'energy': {'pe_max': 18, 'pb_max': 1.5}
        }
        return sector_thresholds.get(sector, {'pe_max': 20, 'pb_max': 1.5})
