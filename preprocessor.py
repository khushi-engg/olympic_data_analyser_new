# preprocessor.py - FIXED FOR BUFFER OVERFLOW ERROR

import pandas as pd
import os
import sys


def preprocess():
    """Load Olympic data with fix for buffer overflow error"""

    print("=" * 50)
    print("PREPROCESSOR STARTED")
    print("=" * 50)

    # Get the directory where this script is located
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"📁 Script directory: {current_dir}")
    except:
        current_dir = os.getcwd()
        print(f"📁 Current working directory: {current_dir}")

    # Streamlit Cloud specific path
    streamlit_cloud_path = '/mount/src/olympic_data_analyser_new/athlete_events.csv'

    print(f"\n🔍 Checking for file at: {streamlit_cloud_path}")

    if os.path.exists(streamlit_cloud_path):
        print(f"✅ File exists! Size: {os.path.getsize(streamlit_cloud_path)} bytes")

        # TRY DIFFERENT READING METHODS TO AVOID BUFFER OVERFLOW
        print("\n📖 Attempting to read with different methods:")

        # Method 1: Use chunks (most reliable for large files)
        try:
            print("   Method 1: Reading with chunks...")
            chunk_iter = pd.read_csv(streamlit_cloud_path,
                                     encoding='latin1',
                                     chunksize=10000,
                                     on_bad_lines='skip')
            df = pd.concat(chunk_iter, ignore_index=True)
            print(f"   ✅ SUCCESS! Loaded {len(df)} rows using chunks")
        except Exception as e:
            print(f"   ❌ Method 1 failed: {e}")
            df = None

        # Method 2: Try with different engine if method 1 failed
        if df is None:
            try:
                print("   Method 2: Reading with python engine...")
                df = pd.read_csv(streamlit_cloud_path,
                                 encoding='latin1',
                                 engine='python',
                                 on_bad_lines='skip')
                print(f"   ✅ SUCCESS! Loaded {len(df)} rows with python engine")
            except Exception as e:
                print(f"   ❌ Method 2 failed: {e}")
                df = None

        # Method 3: Try with low_memory=False
        if df is None:
            try:
                print("   Method 3: Reading with low_memory=False...")
                df = pd.read_csv(streamlit_cloud_path,
                                 encoding='latin1',
                                 low_memory=False,
                                 on_bad_lines='skip')
                print(f"   ✅ SUCCESS! Loaded {len(df)} rows with low_memory=False")
            except Exception as e:
                print(f"   ❌ Method 3 failed: {e}")
                df = None
    else:
        print(f"❌ File NOT found at: {streamlit_cloud_path}")
        return pd.DataFrame(columns=['Year', 'region', 'Medal', 'Sport', 'Name', 'City', 'Event', 'NOC', 'Season'])

    if df is None:
        print("\n❌ CRITICAL: All reading methods failed!")
        return pd.DataFrame(columns=['Year', 'region', 'Medal', 'Sport', 'Name', 'City', 'Event', 'NOC', 'Season'])

    # Load noc_regions.csv
    noc_path = streamlit_cloud_path.replace('athlete_events.csv', 'noc_regions.csv')
    region_df = None

    print(f"\n🔍 Loading noc_regions.csv from: {noc_path}")
    if os.path.exists(noc_path):
        try:
            region_df = pd.read_csv(noc_path, encoding='latin1', on_bad_lines='skip')
            print(f"✅ Loaded {len(region_df)} rows from noc_regions.csv")
        except Exception as e:
            print(f"❌ Error loading noc_regions.csv: {e}")
    else:
        print(f"❌ noc_regions.csv not found at: {noc_path}")

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