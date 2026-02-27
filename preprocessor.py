# preprocessor.py - FINAL VERSION WITH REAL DATA LOADING

import pandas as pd
import os


def preprocess():
    """Load REAL Olympic data - NO SAMPLE DATA FALLBACK"""

    print("=" * 50)
    print("PREPROCESSOR - LOADING REAL OLYMPIC DATA")
    print("=" * 50)

    # Get the current directory
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")

    # List all files to see what's available
    print("\n📋 Files in current directory:")
    for file in os.listdir(current_dir):
        if file.endswith('.csv'):
            size = os.path.getsize(os.path.join(current_dir, file))
            print(f"   📄 {file} - {size} bytes")

    # Path to the CSV files (case sensitive!)
    athlete_path = os.path.join(current_dir, 'athlete_events.csv')
    noc_path = os.path.join(current_dir, 'noc_regions.csv')

    print(f"\n🔍 Looking for athlete_events.csv at: {athlete_path}")

    # Check if files exist
    if not os.path.exists(athlete_path):
        print(f"❌ athlete_events.csv NOT FOUND!")
        print("\n🚨 CANNOT CONTINUE WITHOUT REAL DATA!")
        print("Please ensure athlete_events.csv is in the repository.")
        return pd.DataFrame()

    file_size = os.path.getsize(athlete_path)
    print(f"✅ Found! Size: {file_size} bytes ({file_size / 1e6:.2f} MB)")

    # Try to load the real data
    try:
        print("\n📖 Loading real Olympic data...")

        # For large files, use chunks
        chunks = []
        chunk_count = 0
        for chunk in pd.read_csv(athlete_path, encoding='latin1', chunksize=100000, on_bad_lines='skip'):
            chunk_count += 1
            print(f"   Loaded chunk {chunk_count}: {len(chunk)} rows")
            chunks.append(chunk)

        df = pd.concat(chunks, ignore_index=True)
        print(f"\n✅ SUCCESS! Loaded {len(df)} total rows from REAL DATA")

    except Exception as e:
        print(f"❌ Error loading real data: {e}")
        print("\n🚨 CANNOT CONTINUE WITHOUT REAL DATA!")
        return pd.DataFrame()

    # Load region data
    if os.path.exists(noc_path):
        region_df = pd.read_csv(noc_path, encoding='latin1')
        print(f"✅ Loaded noc_regions.csv with {len(region_df)} rows")
    else:
        print(f"❌ noc_regions.csv NOT FOUND!")
        region_df = None

    # Process the real data
    print("\n🔧 Processing REAL Olympic data...")

    # Filter for Summer Olympics
    if 'Season' in df.columns:
        original_count = len(df)
        df = df[df['Season'] == 'Summer'].copy()
        print(f"✅ Filtered Summer Olympics: {original_count} → {len(df)} rows")

    # Merge with region data
    if region_df is not None and 'NOC' in df.columns and 'NOC' in region_df.columns:
        df = df.merge(region_df[['NOC', 'region']], on='NOC', how='left')
        df['region'] = df['region'].fillna('Unknown')
        print(f"✅ Merged with region data")
    else:
        df['region'] = df['NOC'] if 'NOC' in df.columns else 'Unknown'
        print(f"✅ Created region column from NOC")

    # Create medal columns
    if 'Medal' in df.columns:
        df['Gold'] = (df['Medal'] == 'Gold').astype(int)
        df['Silver'] = (df['Medal'] == 'Silver').astype(int)
        df['Bronze'] = (df['Medal'] == 'Bronze').astype(int)
        print(f"✅ Created medal columns")
    else:
        df['Gold'] = 0
        df['Silver'] = 0
        df['Bronze'] = 0

    # Remove duplicates
    dup_cols = ['Team', 'NOC', 'Games', 'Year', 'Sport', 'Event', 'Medal']
    existing_cols = [col for col in dup_cols if col in df.columns]
    if existing_cols:
        original_count = len(df)
        df = df.drop_duplicates(subset=existing_cols)
        print(f"✅ Removed {original_count - len(df)} duplicates")

    # Final stats
    print(f"\n{'=' * 50}")
    print("✅ REAL OLYMPIC DATA LOADED SUCCESSFULLY!")
    print(f"{'=' * 50}")
    print(f"📊 Total rows: {len(df):,}")
    print(f"📊 Total countries: {df['region'].nunique()}")
    print(f"📊 Year range: {int(df['Year'].min())} - {int(df['Year'].max())}")
    print(f"📊 Total sports: {df['Sport'].nunique()}")
    print(f"{'=' * 50}")

    return df