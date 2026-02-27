# In your preprocessor.py file

import pandas as pd
import os


def preprocess():
    # Check if files exist
    athlete_file = 'athlete_events.csv'
    noc_file = 'noc_regions.csv'

    if not os.path.exists(athlete_file):
        print(f"ERROR: {athlete_file} not found!")
        # Return DataFrame with minimal structure to prevent crashes
        return pd.DataFrame(columns=['Year', 'region', 'Medal', 'NOC', 'Season'])

    # Load data with multiple encoding attempts
    df = None
    for encoding in ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252']:
        try:
            df = pd.read_csv(athlete_file, encoding=encoding, on_bad_lines='skip')
            print(f"✅ Loaded athlete_events.csv with encoding: {encoding}")
            break
        except:
            continue

    if df is None:
        print("ERROR: Could not load athlete_events.csv with any encoding")
        return pd.DataFrame(columns=['Year', 'region', 'Medal', 'NOC', 'Season'])

    # Load region data
    region_df = None
    for encoding in ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252']:
        try:
            region_df = pd.read_csv(noc_file, encoding=encoding, on_bad_lines='skip')
            print(f"✅ Loaded noc_regions.csv with encoding: {encoding}")
            break
        except:
            continue

    # Filter for Summer Olympics if Season column exists
    if 'Season' in df.columns:
        df = df[df['Season'] == 'Summer'].copy()
    else:
        print("⚠️ 'Season' column not found - assuming all data is Summer Olympics")

    # Merge with region data if possible
    if region_df is not None and 'NOC' in df.columns and 'NOC' in region_df.columns:
        df = df.merge(region_df, on='NOC', how='left')
        if 'region' in df.columns:
            df['region'] = df['region'].fillna('Unknown')
    else:
        print("⚠️ Could not merge region data - creating dummy region column")
        df['region'] = 'Unknown'

    # Create medal dummy columns
    if 'Medal' in df.columns:
        medal_dummies = pd.get_dummies(df['Medal'], prefix='', prefix_sep='')
        for medal in ['Gold', 'Silver', 'Bronze']:
            if medal not in medal_dummies.columns:
                medal_dummies[medal] = 0
        df = pd.concat([df, medal_dummies], axis=1)
    else:
        print("⚠️ 'Medal' column not found - creating empty medal columns")
        df['Gold'] = 0
        df['Silver'] = 0
        df['Bronze'] = 0

    # Remove duplicates
    df = df.drop_duplicates()

    print(f"✅ Preprocessing complete! DataFrame shape: {df.shape}")
    print(f"✅ Columns: {df.columns.tolist()}")

    return df