from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import crud, models
from app.database.database import get_db
from app.scoring.value_metrics import EnhancedValueScorer

router = APIRouter()

@router.get("/screening/value-stocks")
async def screen_value_stocks(
    min_score: float = Query(70, description="Score minimo"),
    max_pe: Optional[float] = Query(None, description="P/E massimo"),
    max_pb: Optional[float] = Query(None, description="P/B massimo"),
    min_dividend_yield: Optional[float] = Query(None, description="Dividend yield minimo"),
    max_debt_equity: Optional[float] = Query(None, description="Debt/Equity massimo"),
    min_market_cap: float = Query(500e6, description="Market cap minimo"),
    sector: Optional[str] = Query(None, description="Filtro settore"),
    db: Session = Depends(get_db)
):
    """
    Screening avanzato per value stocks con filtri multipli
    """
    stock_crud = crud.StockCRUD(db)
    
    # Query base
    query = db.query(models.ValueScore).join(models.Stock)
    
    # Applica filtri
    query = query.filter(models.ValueScore.total_score >= min_score)
    query = query.filter(models.Stock.market_cap >= min_market_cap)
    
    if max_pe:
        query = query.filter(models.ValueScore.pe_score >= 50)  # Filtro indiretto su P/E
    
    if sector:
        query = query.filter(models.Stock.sector == sector)
    
    # Esegui query
    results = query.order_by(models.ValueScore.total_score.desc()).limit(100).all()
    
    return {
        "count": len(results),
        "filters_applied": {
            "min_score": min_score,
            "min_market_cap": min_market_cap,
            "sector": sector
        },
        "stocks": [
            {
                "symbol": result.stock.symbol,
                "company_name": result.stock.company_name,
                "sector": result.stock.sector,
                "total_score": result.total_score,
                "component_scores": {
                    "pe": result.pe_score,
                    "pb": result.pb_score,
                    "roe": result.roe_score
                },
                "market_cap": result.stock.market_cap
            }
            for result in results
        ]
    }

@router.get("/stocks/{symbol}/analysis")
async def get_stock_analysis(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Analisi completa di un singolo stock
    """
    stock_crud = crud.StockCRUD(db)
    scorer = EnhancedValueScorer()
    
    stock = stock_crud.get_stock_by_symbol(symbol)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock non trovato")
    
    # Recupera dati fondamentali più recenti
    latest_fundamentals = (db.query(models.FundamentalData)
                          .filter(models.FundamentalData.stock_id == stock.id)
                          .order_by(models.FundamentalData.fiscal_date.desc())
                          .first())
    
    if not latest_fundamentals:
        raise HTTPException(status_code=404, detail="Dati fondamentali non trovati")
    
    # Calcola score
    fundamentals_model = Fundamentals(
        pe_ratio=latest_fundamentals.pe_ratio,
        price_to_book_ratio=latest_fundamentals.price_to_book,
        price_to_sales_ratio=latest_fundamentals.price_to_sales,
        ev_to_ebitda=latest_fundamentals.ev_to_ebitda,
        debt_to_equity=latest_fundamentals.debt_to_equity,
        return_on_equity=latest_fundamentals.return_on_equity,
        dividend_yield=latest_fundamentals.dividend_yield
    )
    
    value_score = scorer.calculate_score(fundamentals_model, stock.sector)
    
    return {
        "stock_info": {
            "symbol": stock.symbol,
            "company_name": stock.company_name,
            "sector": stock.sector,
            "industry": stock.industry,
            "market_cap": stock.market_cap
        },
        "fundamentals": fundamentals_model.dict(),
        "value_analysis": {
            "total_score": value_score.total_score,
            "component_scores": value_score.component_scores,
            "warnings": value_score.warnings,
            "strengths": value_score.strengths,
            "rating": self._get_rating_description(value_score.total_score)
        },
        "historical_scores": self._get_historical_scores(db, stock.id)
    }
    
    def _get_rating_description(self, score: float) -> str:
        if score >= 80:
            return "STRONG_BUY"
        elif score >= 70:
            return "BUY"
        elif score >= 60:
            return "HOLD"
        elif score >= 50:
            return "WEAK_HOLD"
        else:
            return "SELL"
    
    def _get_historical_scores(self, db: Session, stock_id: int):
        scores = (db.query(models.ValueScore)
                 .filter(models.ValueScore.stock_id == stock_id)
                 .order_by(models.ValueScore.score_date.desc())
                 .limit(10)
                 .all())
        
        return [
            {
                "date": score.score_date.isoformat(),
                "total_score": score.total_score,
                "pe_score": score.pe_score
            }
            for score in scores
        ]
