## preprocessor.py - USING PRE-PROCESSED DATA

import pandas as pd
import os

def preprocess():
    """Load pre-processed Olympic data"""

    print("=" * 50)
    print("PREPROCESSOR - USING PRE-PROCESSED DATA")
    print("=" * 50)

    current_dir = '/mount/src/olympic_data_analyser_new'
    print(f"📁 Current directory: {current_dir}")

    # Try to load pre-processed data first (compressed)
    processed_path = os.path.join(current_dir, 'processed_olympic_data.csv.gz')
    sample_path = os.path.join(current_dir, 'sample_olympic_data.csv')

    # Method 1: Load compressed processed data
    if os.path.exists(processed_path):
        print(f"✅ Found processed data: {processed_path}")
        try:
            df = pd.read_csv(processed_path, compression='gzip')
            print(f"✅ Loaded {len(df)} rows from processed data")
            print(f"✅ Columns: {df.columns.tolist()}")
            return df
        except Exception as e:
            print(f"❌ Error loading processed data: {e}")

    # Method 2: Load sample data
    if os.path.exists(sample_path):
        print(f"✅ Found sample data: {sample_path}")
        try:
            df = pd.read_csv(sample_path)
            print(f"✅ Loaded {len(df)} rows from sample data")
            return df
        except Exception as e:
            print(f"❌ Error loading sample data: {e}")

    # Method 3: Create minimal sample data
    print("⚠️ No pre-processed files found, creating minimal sample")
    return create_minimal_sample()


def create_minimal_sample():
    """Create minimal sample data"""
    import numpy as np

    years = [2000, 2004, 2008, 2012, 2016]
    countries = ['USA', 'CHN', 'RUS', 'GBR', 'GER', 'FRA', 'ITA', 'AUS', 'JPN', 'CAN']
    regions = ['United States', 'China', 'Russia', 'Great Britain', 'Germany',
               'France', 'Italy', 'Australia', 'Japan', 'Canada']
    sports = ['Athletics', 'Swimming', 'Gymnastics']

    data = []
    for year in years:
        for sport in sports:
            for noc, region in zip(countries, regions):
                for medal in ['Gold', 'Silver', 'Bronze']:
                    if np.random.random() > 0.5:  # 50% chance
                        data.append({
                            'Year': year,
                            'Sport': sport,
                            'Event': f"{sport} Event",
                            'NOC': noc,
                            'region': region,
                            'Medal': medal,
                            'Name': f"{region} Athlete",
                            'Gold': 1 if medal == 'Gold' else 0,
                            'Silver': 1 if medal == 'Silver' else 0,
                            'Bronze': 1 if medal == 'Bronze' else 0
                        })

    df = pd.DataFrame(data)
    print(f"✅ Created {len(df)} rows of minimal sample data")
    return df