from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    company_name = Column(String(255))
    sector = Column(String(100))
    industry = Column(String(100))
    exchange = Column(String(50))
    country = Column(String(50))
    market_cap = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class FundamentalData(Base):
    __tablename__ = "fundamental_data"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, index=True)
    period = Column(String(20))  # 'annual' or 'quarterly'
    fiscal_date = Column(DateTime)
    reported_date = Column(DateTime)
    
    # Metriche fondamentali
    revenue = Column(Float)
    net_income = Column(Float)
    eps = Column(Float)
    pe_ratio = Column(Float)
    price_to_book = Column(Float)
    price_to_sales = Column(Float)
    ev_to_ebitda = Column(Float)
    debt_to_equity = Column(Float)
    return_on_equity = Column(Float)
    dividend_yield = Column(Float)
    free_cash_flow = Column(Float)
    
    created_at = Column(DateTime, default=func.now())

class ValueScore(Base):
    __tablename__ = "value_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, index=True)
    score_date = Column(DateTime, default=func.now())
    total_score = Column(Float)
    
    # Score componenti
    pe_score = Column(Float)
    pb_score = Column(Float)
    ps_score = Column(Float)
    ev_ebitda_score = Column(Float)
    debt_equity_score = Column(Float)
    roe_score = Column(Float)
    dividend_score = Column(Float)
    
    # Metadata
    warnings = Column(Text)  # JSON string di warnings
    strengths = Column(Text)  # JSON string di strengths
    sector_percentile = Column(Float)
    
    created_at = Column(DateTime, default=func.now())
