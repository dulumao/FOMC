# Main Application for FOMC Project

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """
    Main function to run the FOMC application
    """
    print("Federal mOnetary llM Committee (FOMC) System")
    print("===========================================")
    print("Initializing system components...")
    
    # Check if required environment variables are set
    fred_api_key = os.getenv("FRED_API_KEY")
    if not fred_api_key or fred_api_key == "your_fred_api_key_here":
        print("WARNING: FRED API key not set in .env file")
        print("Please update the .env file with your actual FRED API key")
    
    print("Using SQLite database: fomc_data.db")
    
    print("\nSystem ready. Please refer to README.md for implementation roadmap.")
    
if __name__ == "__main__":
    main()