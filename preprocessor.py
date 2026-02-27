# preprocessor.py - ULTIMATE VERSION FOR STREAMLIT CLOUD

import pandas as pd
import os
import sys


def preprocess():
    """Load Olympic data with ultimate path handling for Streamlit Cloud"""

    # Print debug info that will be captured by app.py
    print("=" * 50)
    print("PREPROCESSOR STARTED")
    print("=" * 50)

    # Get the directory where this script is located
    try:
        # For local development
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"📁 Script directory: {current_dir}")
    except:
        # For Streamlit Cloud
        current_dir = os.getcwd()
        print(f"📁 Current working directory: {current_dir}")

    # List all files in current directory (for debugging)
    print("\n📋 Files in current directory:")
    try:
        for file in os.listdir(current_dir):
            size = os.path.getsize(os.path.join(current_dir, file)) if os.path.isfile(
                os.path.join(current_dir, file)) else 0
            print(f"   - {file} ({size} bytes)")
    except:
        print("   Could not list directory contents")

    # SPECIFIC PATH FOR STREAMLIT CLOUD (from your error logs)
    streamlit_cloud_base = '/mount/src/olympic_data_analyser_new'

    # Try multiple possible paths for the CSV files - ORDERED BY LIKELIHOOD
    possible_paths = [
        # Streamlit Cloud specific path (MOST LIKELY)
        os.path.join(streamlit_cloud_base, 'athlete_events.csv'),

        # Current directory
        os.path.join(current_dir, 'athlete_events.csv'),

        # Parent directory
        os.path.join(os.path.dirname(current_dir), 'athlete_events.csv'),

        # Data subdirectory
        os.path.join(current_dir, 'data', 'athlete_events.csv'),

        # Relative path
        'athlete_events.csv',

        # Absolute path from root (just in case)
        '/athlete_events.csv',
    ]

    # Load athlete_events.csv
    df = None
    athlete_path = None

    print("\n🔍 Searching for athlete_events.csv...")
    for i, path in enumerate(possible_paths, 1):
        print(f"   Path {i}: {path}")
        if os.path.exists(path):
            print(f"   ✅ FOUND at: {path}")
            athlete_path = path
            try:
                df = pd.read_csv(path, encoding='latin1', on_bad_lines='skip')
                print(f"   ✅ Loaded {len(df)} rows")
                break
            except Exception as e:
                print(f"   ❌ Error reading: {e}")
                continue
        else:
            print(f"   ❌ Not found")

    if df is None:
        print("\n❌ CRITICAL: Could not find athlete_events.csv in any location!")
        print("Returning empty DataFrame with required columns")
        return pd.DataFrame(columns=['Year', 'region', 'Medal', 'Sport', 'Name', 'City', 'Event', 'NOC', 'Season'])

    # Load noc_regions.csv
    region_df = None
    print("\n🔍 Searching for noc_regions.csv...")

    for i, path in enumerate(possible_paths, 1):
        noc_path = path.replace('athlete_events.csv', 'noc_regions.csv')
        print(f"   Path {i}: {noc_path}")
        if os.path.exists(noc_path):
            print(f"   ✅ FOUND at: {noc_path}")
            try:
                region_df = pd.read_csv(noc_path, encoding='latin1', on_bad_lines='skip')
                print(f"   ✅ Loaded {len(region_df)} rows")
                break
            except Exception as e:
                print(f"   ❌ Error reading: {e}")
                continue
        else:
            print(f"   ❌ Not found")

    # Filter for Summer Olympics
    print("\n🔧 Processing data...")
    if 'Season' in df.columns:
        original_count = len(df)
        df = df[df['Season'] == 'Summer']
        print(f"   ✅ Filtered Summer Olympics: {original_count} → {len(df)} rows")
    else:
        print("   ⚠️ 'Season' column not found, skipping filter")

    # Merge with region data
    if region_df is not None and 'NOC' in df.columns and 'NOC' in region_df.columns:
        print(f"   ✅ Merging with region data...")
        df = df.merge(region_df, on='NOC', how='left')
        if 'region' in df.columns:
            df['region'] = df['region'].fillna('Unknown')
            print(f"   ✅ Region column created")
    else:
        print(f"   ⚠️ Creating dummy region column")
        df['region'] = df['NOC'] if 'NOC' in df.columns else 'Unknown'

    # Create medal dummy columns
    if 'Medal' in df.columns:
        print(f"   ✅ Creating medal dummy columns...")
        medal_dummies = pd.get_dummies(df['Medal'])
        for medal in ['Gold', 'Silver', 'Bronze']:
            if medal not in medal_dummies.columns:
                medal_dummies[medal] = 0
        df = pd.concat([df, medal_dummies], axis=1)
        print(f"   ✅ Medal columns: Gold, Silver, Bronze")
    else:
        print(f"   ⚠️ 'Medal' column not found, creating empty medal columns")
        df['Gold'] = 0
        df['Silver'] = 0
        df['Bronze'] = 0

    # Ensure all required columns exist
    print(f"   ✅ Ensuring required columns exist...")
    required_cols = ['Year', 'region', 'Medal', 'Sport', 'Name', 'City', 'Event', 'NOC']
    for col in required_cols:
        if col not in df.columns:
            if col == 'Year':
                df[col] = 2016
                print(f"   ⚠️ Added missing column '{col}' with default value 2016")
            elif col == 'City':
                df[col] = 'Unknown'
                print(f"   ⚠️ Added missing column '{col}' with default value 'Unknown'")
            elif col == 'Event':
                df[col] = df['Sport'] + ' - Event' if 'Sport' in df.columns else 'Unknown'
                print(f"   ⚠️ Added missing column '{col}'")
            else:
                df[col] = 'Unknown'
                print(f"   ⚠️ Added missing column '{col}' with default value 'Unknown'")

    # Remove duplicates
    original_count = len(df)
    df = df.drop_duplicates()
    print(f"   ✅ Removed {original_count - len(df)} duplicates")

    # Final summary
    print("\n" + "=" * 50)
    print("PREPROCESSOR COMPLETED SUCCESSFULLY")
    print("=" * 50)
    print(f"📊 Final DataFrame shape: {df.shape}")
    print(f"📊 Final columns: {df.columns.tolist()}")

    # Critical column check
    print("\n🔍 CRITICAL COLUMN CHECK:")
    if 'Year' in df.columns:
        print(f"   ✅ 'Year' column EXISTS")
        print(f"   📅 Year range: {int(df['Year'].min())} to {int(df['Year'].max())}")
    else:
        print(f"   ❌ 'Year' column MISSING - THIS WILL CAUSE ERRORS!")

    if 'region' in df.columns:
        print(f"   ✅ 'region' column EXISTS")
        print(f"   🌍 Number of regions: {df['region'].nunique()}")
    else:
        print(f"   ❌ 'region' column MISSING")

    print("=" * 50)

    return df