# preprocessor.py - UPDATED VERSION

import pandas as pd
import os


def preprocess():
    # Get the current directory where this script is running
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Print debug info
    print(f"Current directory: {current_dir}")
    print(f"Files in directory: {os.listdir(current_dir)}")

    # Try different possible paths for the CSV files
    possible_paths = [
        os.path.join(current_dir, 'athlete_events.csv'),
        os.path.join(current_dir, 'data', 'athlete_events.csv'),
        os.path.join(current_dir, '..', 'athlete_events.csv'),
        'athlete_events.csv',  # relative path
        '/mount/src/olympic_data_analyser_new/athlete_events.csv',  # absolute path from your error
    ]

    df = None
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found athlete_events.csv at: {path}")
            try:
                df = pd.read_csv(path, encoding='latin1', on_bad_lines='skip')
                print(f"✅ Loaded {len(df)} rows")
                break
            except Exception as e:
                print(f"❌ Error reading {path}: {e}")
                continue

    if df is None:
        print("❌ Could not find athlete_events.csv in any location!")
        # Return empty DataFrame with required columns to prevent crashes
        return pd.DataFrame(columns=['Year', 'region', 'Medal', 'Sport', 'Name', 'City', 'Event', 'NOC', 'Season'])

    # Load region data
    region_df = None
    for path in possible_paths:
        if 'noc_regions.csv' in path or path.replace('athlete_events.csv', 'noc_regions.csv'):
            region_path = path.replace('athlete_events.csv', 'noc_regions.csv')
            if os.path.exists(region_path):
                print(f"✅ Found noc_regions.csv at: {region_path}")
                try:
                    region_df = pd.read_csv(region_path, encoding='latin1', on_bad_lines='skip')
                    print(f"✅ Loaded {len(region_df)} rows")
                    break
                except:
                    continue

    # If region_df not found, try direct path
    if region_df is None:
        region_path = os.path.join(current_dir, 'noc_regions.csv')
        if os.path.exists(region_path):
            region_df = pd.read_csv(region_path, encoding='latin1', on_bad_lines='skip')

    # Filter for Summer Olympics
    if 'Season' in df.columns:
        df = df[df['Season'] == 'Summer']

    # Merge with region data
    if region_df is not None and 'NOC' in df.columns and 'NOC' in region_df.columns:
        df = df.merge(region_df, on='NOC', how='left')
        if 'region' in df.columns:
            df['region'] = df['region'].fillna('Unknown')
    else:
        # Create dummy region column if merge fails
        df['region'] = 'Unknown'

    # Create medal dummy columns
    if 'Medal' in df.columns:
        medal_dummies = pd.get_dummies(df['Medal'])
        for medal in ['Gold', 'Silver', 'Bronze']:
            if medal not in medal_dummies.columns:
                medal_dummies[medal] = 0
        df = pd.concat([df, medal_dummies], axis=1)
    else:
        df['Gold'] = 0
        df['Silver'] = 0
        df['Bronze'] = 0

    # Ensure all required columns exist
    required_cols = ['Year', 'region', 'Medal', 'Sport', 'Name', 'City', 'Event', 'NOC']
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    df = df.drop_duplicates()
    print(f"✅ Final DataFrame shape: {df.shape}")

    return df