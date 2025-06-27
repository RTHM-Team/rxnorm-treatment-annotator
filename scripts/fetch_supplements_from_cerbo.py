#!/usr/bin/env python3
"""
Fetch Supplements from Cerbo EHR API

This script fetches all supplements from the Cerbo EHR API and saves them
to a CSV file for use in treatment annotation.

Usage:
    python fetch_supplements_from_cerbo.py

Configuration:
    Set CERBO_USERNAME and CERBO_PASSWORD environment variables
    or modify the script to include credentials directly (not recommended)
"""

import requests
import pandas as pd
import base64
import os
import time
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

def get_auth_header(username: str = None, password: str = None, api_key: str = None) -> str:
    """Create auth header from username/password or API key"""
    if api_key:
        # If API key is provided and already includes 'Basic ', use as-is
        if api_key.startswith('Basic '):
            return api_key
        else:
            # Otherwise assume it's a bearer token
            return f"Bearer {api_key}"
    elif username and password:
        # Use basic auth
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    else:
        raise ValueError("Either API key or username/password must be provided")

def fetch_supplements_page(auth_header: str, limit: int = 100, offset: int = 0, 
                          active_only: bool = True) -> Dict:
    """Fetch a single page of supplements from the API"""
    
    url = "https://rthmehr.md-hq.com/api/v1/supplements"
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    params = {
        "limit": limit,
        "offset": offset
    }
    
    if active_only:
        params["active_only"] = "true"
    
    try:
        print(f"Fetching supplements: offset={offset}, limit={limit}")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise Exception("Authentication failed. Please check your credentials.")
        elif response.status_code == 404:
            raise Exception("API endpoint not found. Please check the URL.")
        else:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")

def fetch_all_supplements(username: str = None, password: str = None, api_key: str = None, active_only: bool = True) -> List[Dict]:
    """Fetch all supplements using pagination"""
    
    print("=== FETCHING SUPPLEMENTS FROM CERBO EHR ===\n")
    
    auth_header = get_auth_header(username, password, api_key)
    all_supplements = []
    
    offset = 0
    limit = 100  # API maximum
    
    while True:
        try:
            # Add a small delay to be respectful to the API
            if offset > 0:
                time.sleep(0.5)
            
            response_data = fetch_supplements_page(auth_header, limit, offset, active_only)
            
            # Check if response has supplements data
            if 'data' in response_data:
                supplements = response_data['data']
            elif isinstance(response_data, list):
                supplements = response_data
            else:
                print(f"Unexpected response format: {response_data}")
                break
            
            if not supplements or len(supplements) == 0:
                print("No more supplements to fetch.")
                break
            
            all_supplements.extend(supplements)
            print(f"  Fetched {len(supplements)} supplements (total: {len(all_supplements)})")
            
            # Check if we got fewer results than the limit (indicates last page)
            if len(supplements) < limit:
                print("Reached last page of results.")
                break
            
            offset += limit
            
            # Safety check to prevent infinite loops
            if len(all_supplements) > 10000:
                print("⚠️ Fetched over 10,000 supplements. Stopping as safety measure.")
                break
                
        except Exception as e:
            print(f"❌ Error fetching supplements at offset {offset}: {str(e)}")
            break
    
    print(f"\n✅ Successfully fetched {len(all_supplements)} supplements total")
    return all_supplements

def process_supplements_data(supplements: List[Dict]) -> pd.DataFrame:
    """Process raw supplement data into structured DataFrame"""
    
    print("Processing supplements data...")
    
    processed_supplements = []
    
    for supplement in supplements:
        # Extract key fields (adjust based on actual API response structure)
        processed = {
            'supplement_id': supplement.get('id', ''),
            'name': supplement.get('name', ''),
            'vendor_code': supplement.get('vendor_code', ''),
            'class': supplement.get('class', ''),
            'external_ref_id': supplement.get('external_ref_id', ''),
            'active': supplement.get('active', True),
            'description': supplement.get('description', ''),
            'vendor': supplement.get('vendor', ''),
            'dosage_form': supplement.get('dosage_form', ''),
            'strength': supplement.get('strength', ''),
            'unit': supplement.get('unit', ''),
        }
        
        # Add any additional fields that might be present
        for key, value in supplement.items():
            if key not in processed:
                processed[f'additional_{key}'] = value
        
        processed_supplements.append(processed)
    
    df = pd.DataFrame(processed_supplements)
    
    # Remove completely empty columns
    df = df.dropna(axis=1, how='all')
    
    print(f"✅ Processed {len(df)} supplements into structured format")
    return df

def save_supplements_data(df: pd.DataFrame, output_file: str = 'cerbo_supplements.csv'):
    """Save supplements data to CSV file"""
    
    # Save main supplements file
    df.to_csv(output_file, index=False)
    print(f"✅ Saved supplements to: {output_file}")
    
    # Also save to data directory for integration
    data_output = f'data/{output_file}'
    df.to_csv(data_output, index=False)
    print(f"✅ Saved supplements to: {data_output}")
    
    # Create summary statistics
    print(f"\n=== SUPPLEMENTS SUMMARY ===")
    print(f"Total supplements: {len(df):,}")
    
    if 'active' in df.columns:
        active_count = df['active'].sum() if df['active'].dtype == bool else len(df[df['active'] == True])
        print(f"Active supplements: {active_count:,}")
    
    if 'class' in df.columns:
        class_counts = df['class'].value_counts()
        print(f"Top supplement classes:")
        for class_name, count in class_counts.head(5).items():
            print(f"  {class_name}: {count:,}")
    
    if 'vendor' in df.columns:
        vendor_counts = df['vendor'].value_counts()
        print(f"Top vendors:")
        for vendor, count in vendor_counts.head(5).items():
            print(f"  {vendor}: {count:,}")
    
    return output_file

def main():
    """Main function to fetch and process supplements"""
    
    print("Cerbo EHR Supplements Fetcher")
    print("=" * 40)
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials from environment variables
    api_key = os.getenv('CERBO_API_KEY')
    username = os.getenv('CERBO_USERNAME')
    password = os.getenv('CERBO_PASSWORD')
    
    if not api_key and not (username and password):
        print("\n⚠️ Credentials not found in .env file or environment variables.")
        print("Please set CERBO_API_KEY in .env file or set CERBO_USERNAME and CERBO_PASSWORD.")
        print("\nIn .env file:")
        print('CERBO_API_KEY="your_api_key_here"')
        print("\nOr as environment variables:")
        print("export CERBO_USERNAME='your_username'")
        print("export CERBO_PASSWORD='your_password'")
        return 1
    
    try:
        # Fetch all supplements
        supplements = fetch_all_supplements(username, password, api_key, active_only=True)
        
        if not supplements:
            print("❌ No supplements were fetched")
            return 1
        
        # Process into DataFrame
        df = process_supplements_data(supplements)
        
        # Save to CSV
        output_file = save_supplements_data(df)
        
        print(f"\n🎉 SUCCESS!")
        print(f"   Fetched and saved {len(df):,} supplements")
        print(f"   Output file: {output_file}")
        print(f"   Ready for integration with treatment annotation system")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())