# FRED API Integration for FOMC Project

import os
import requests
import pandas as pd
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FredAPI:
    """
    Class to interact with the FRED API
    """
    
    def __init__(self):
        """
        Initialize the FRED API client
        """
        self.api_key = os.getenv("FRED_API_KEY")
        if not self.api_key:
            raise ValueError("FRED_API_KEY not found in environment variables")
        
        self.base_url = "https://api.stlouisfed.org/fred"
    
    def get_series(self, series_id: str, 
                   observation_start: Optional[str] = None,
                   observation_end: Optional[str] = None,
                   frequency: Optional[str] = None,
                   units: Optional[str] = None) -> Dict:
        """
        Get economic data series from FRED
        
        Args:
            series_id: The FRED series ID
            observation_start: Start date (YYYY-MM-DD)
            observation_end: End date (YYYY-MM-DD)
            frequency: Data frequency (daily, weekly, monthly, quarterly, annual)
            units: Units of measurement (lin, chg, ch1, pch, pc1, pca, cch, gpta, gpca)
            
        Returns:
            Dictionary with series information and data
        """
        url = f"{self.base_url}/series/observations"
        
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }
        
        if observation_start:
            params['observation_start'] = observation_start
        if observation_end:
            params['observation_end'] = observation_end
        if frequency:
            params['frequency'] = frequency
        if units:
            params['units'] = units
            
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def get_series_info(self, series_id: str) -> Dict:
        """
        Get metadata information about a series
        
        Args:
            series_id: The FRED series ID
            
        Returns:
            Dictionary with series metadata
        """
        url = f"{self.base_url}/series"
        
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def search_series(self, search_text: str, limit: int = 30) -> Dict:
        """
        Search for economic series in FRED
        
        Args:
            search_text: Text to search for
            limit: Maximum number of results to return
            
        Returns:
            Dictionary with search results
        """
        url = f"{self.base_url}/series/search"
        
        params = {
            'search_text': search_text,
            'api_key': self.api_key,
            'file_type': 'json',
            'limit': limit
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def series_to_dataframe(self, series_data: Dict) -> pd.DataFrame:
        """
        Convert series data to pandas DataFrame
        
        Args:
            series_data: Series data from get_series method
            
        Returns:
            DataFrame with date and value columns
        """
        observations = series_data['observations']
        df = pd.DataFrame(observations)
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        return df[['date', 'value']].dropna()

# Example usage:
# fred = FredAPI()
# gdp_data = fred.get_series('GDP', observation_start='2020-01-01')
# gdp_df = fred.series_to_dataframe(gdp_data)