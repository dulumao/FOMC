# Database models for FOMC project

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from .base import Base

class EconomicIndicator(Base):
    """
    Model for storing economic indicators from FRED
    """
    __tablename__ = 'economic_indicators'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)  # FRED series ID
    description = Column(Text)
    frequency = Column(String(20))  # Daily, Weekly, Monthly, Quarterly, Annual
    units = Column(String(50))
    seasonal_adjustment = Column(String(50))
    last_updated = Column(DateTime)
    data = Column(Text)  # JSON string of time series data
    
    def __repr__(self):
        return f"<EconomicIndicator(name='{self.name}', code='{self.code}')>"

class EconomicDataPoint(Base):
    """
    Model for individual data points of economic indicators
    """
    __tablename__ = 'economic_data_points'
    
    id = Column(Integer, primary_key=True)
    indicator_id = Column(Integer, nullable=False)  # Foreign key to EconomicIndicator
    date = Column(DateTime, nullable=False)
    value = Column(Float)
    
    def __repr__(self):
        return f"<EconomicDataPoint(indicator_id={self.indicator_id}, date='{self.date}', value={self.value})>"