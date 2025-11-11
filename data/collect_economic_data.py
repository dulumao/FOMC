# Data Collection Script for FOMC Project
# Collects important economic and financial indicators for monetary policy decision making

import sys
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.fred_api import FredAPI
from data.preprocessing import DataPreprocessor
from database.connection import get_db, init_db, engine
from database.base import Base
from database.models import EconomicIndicator, EconomicDataPoint

# Load environment variables
load_dotenv()

def get_key_economic_indicators():
    """
    Returns a dictionary of key economic indicators important for monetary policy decisions
    """
    return {
        # Employment indicators
        'UNRATE': {
            'name': '失业率',
            'description': 'Civilian Unemployment Rate',
            'frequency': 'Monthly',
            'units': 'Percent'
        },
        'NROU': {
            'name': '自然失业率',
            'description': 'Natural Rate of Unemployment (Long-Term)',
            'frequency': 'Quarterly',
            'units': 'Percent'
        },
        'PAYEMS': {
            'name': '非农就业人数',
            'description': 'All Employees, Total Nonfarm',
            'frequency': 'Monthly',
            'units': 'Thousands of Persons'
        },
        
        # Inflation indicators
        'CPIAUCSL': {
            'name': '消费者价格指数',
            'description': 'Consumer Price Index for All Urban Consumers: All Items in U.S. City Average',
            'frequency': 'Monthly',
            'units': 'Index 1982-1984=100'
        },
        'PCEPI': {
            'name': '个人消费支出价格指数',
            'description': 'Personal Consumption Expenditures Price Index',
            'frequency': 'Monthly',
            'units': 'Index 2012=100'
        },
        'PCEPILFE': {
            'name': '核心个人消费支出价格指数',
            'description': 'Personal Consumption Expenditures Price Index Excluding Food and Energy',
            'frequency': 'Monthly',
            'units': 'Index 2012=100'
        },
        'GDPDEF': {
            'name': 'GDP平减指数',
            'description': 'Gross Domestic Product: Implicit Price Deflator',
            'frequency': 'Quarterly',
            'units': 'Index 2012=100'
        },
        
        # GDP and economic activity
        'GDP': {
            'name': '国内生产总值',
            'description': 'Gross Domestic Product',
            'frequency': 'Quarterly',
            'units': 'Billions of Dollars'
        },
        'GDPC1': {
            'name': '实际国内生产总值',
            'description': 'Real Gross Domestic Product',
            'frequency': 'Quarterly',
            'units': 'Billions of Chained 2012 Dollars'
        },
        'INDPRO': {
            'name': '工业生产指数',
            'description': 'Industrial Production Index',
            'frequency': 'Monthly',
            'units': 'Index 2012=100'
        },
        
        # Interest rates
        'DFF': {
            'name': '有效联邦基金利率',
            'description': 'Effective Federal Funds Rate',
            'frequency': 'Daily',
            'units': 'Percent'
        },
        'DTB3': {
            'name': '3个月国债利率',
            'description': '3-Month Treasury Bill: Secondary Market Rate',
            'frequency': 'Daily',
            'units': 'Percent'
        },
        'DGS10': {
            'name': '10年期国债收益率',
            'description': '10-Year Treasury Constant Maturity Rate',
            'frequency': 'Daily',
            'units': 'Percent'
        },
        'T10Y2Y': {
            'name': '10年-2年国债收益率差',
            'description': '10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity',
            'frequency': 'Daily',
            'units': 'Percent'
        },
        
        # Consumer and business sentiment
        'UMCSENT': {
            'name': '密歇根大学消费者信心指数',
            'description': 'University of Michigan: Consumer Sentiment',
            'frequency': 'Monthly',
            'units': 'Index 1966:Q1=100'
        },
        
        # Money supply and banking
        'BOGMBASE': {
            'name': '基础货币',
            'description': 'St. Louis Adjusted Monetary Base',
            'frequency': 'Weekly',
            'units': 'Billions of Dollars'
        },
        'M2SL': {
            'name': 'M2货币供应量',
            'description': 'M2 Money Stock',
            'frequency': 'Weekly',
            'units': 'Billions of Dollars'
        },
        
        # Housing market
        'CSUSHPINSA': {
            'name': 'Case-Shiller房价指数',
            'description': 'S&P/Case-Shiller U.S. National Home Price Index',
            'frequency': 'Monthly',
            'units': 'Index Jan 2000=100'
        }
    }

def initialize_database():
    """
    Initialize the database by creating tables
    """
    print("Initializing database...")
    try:
        # Create tables directly using Base metadata
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
        # Force commit to ensure tables are created
        from sqlalchemy import text
        db = next(get_db())
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def collect_and_store_economic_data(start_date='2025-01-01'):
    """
    Collect economic data from FRED and store it in the database
    """
    print(f"Collecting economic data from {start_date} onwards...")
    
    # Initialize FRED API client
    try:
        fred = FredAPI()
        print("FRED API client initialized successfully.")
    except Exception as e:
        print(f"Error initializing FRED API client: {e}")
        return
    
    # Initialize data preprocessor
    preprocessor = DataPreprocessor()
    
    # Get key economic indicators
    indicators = get_key_economic_indicators()
    print(f"Found {len(indicators)} key economic indicators to collect.")
    
    # Initialize database
    if not initialize_database():
        print("Failed to initialize database. Exiting...")
        return
    
    # Get database session
    try:
        db = next(get_db())
    except Exception as e:
        print(f"Error getting database session: {e}")
        return
    
    collected_count = 0
    
    try:
        for series_id, info in indicators.items():
            print(f"\nCollecting data for {info['name']} ({series_id})...")
            
            try:
                # Get series information
                series_info = fred.get_series_info(series_id)
                if 'seriess' in series_info and len(series_info['seriess']) > 0:
                    fred_info = series_info['seriess'][0]
                else:
                    fred_info = {}
                
                # Check if indicator already exists in database
                existing_indicator = db.query(EconomicIndicator).filter(
                    EconomicIndicator.code == series_id
                ).first()
                
                if existing_indicator:
                    print(f"Indicator {series_id} already exists in database. Updating...")
                    indicator = existing_indicator
                else:
                    # Create new indicator record
                    indicator = EconomicIndicator(
                        name=info['name'],
                        code=series_id,
                        description=info.get('description', fred_info.get('title', '')),
                        frequency=info.get('frequency', fred_info.get('frequency', '')),
                        units=info.get('units', fred_info.get('units', '')),
                        seasonal_adjustment=fred_info.get('seasonal_adjustment', '')
                    )
                    db.add(indicator)
                    db.flush()  # Get the ID without committing
                
                # Get series data
                series_data = fred.get_series(
                    series_id, 
                    observation_start=start_date
                )
                
                if 'observations' not in series_data or len(series_data['observations']) == 0:
                    print(f"No data available for {series_id}")
                    continue
                
                # Convert to DataFrame
                df = fred.series_to_dataframe(series_data)
                
                # Clean data
                df_clean = preprocessor.clean_series(df)
                
                # Delete existing data points for this indicator
                db.query(EconomicDataPoint).filter(
                    EconomicDataPoint.indicator_id == indicator.id
                ).delete()
                
                # Store data points
                data_points = []
                for _, row in df_clean.iterrows():
                    data_point = EconomicDataPoint(
                        indicator_id=indicator.id,
                        date=row['date'],
                        value=row['value']
                    )
                    data_points.append(data_point)
                
                db.add_all(data_points)
                db.commit()
                
                print(f"Successfully collected and stored {len(data_points)} data points for {info['name']}")
                collected_count += 1
                
            except Exception as e:
                print(f"Error collecting data for {series_id}: {e}")
                db.rollback()
                continue
        
        print(f"\nData collection completed. Successfully processed {collected_count} out of {len(indicators)} indicators.")
        
    except Exception as e:
        print(f"Error during data collection: {e}")
    finally:
        # Close database session
        try:
            db.close()
        except:
            pass

if __name__ == "__main__":
    # Initialize database first
    if not initialize_database():
        print("Failed to initialize database. Exiting...")
        sys.exit(1)
    
    # Collect data from 2025-01-01 onwards
    collect_and_store_economic_data('2025-01-01')