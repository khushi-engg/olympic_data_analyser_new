# preprocessor.py - SPECIAL STREAMLIT CLOUD VERSION

import pandas as pd
import os
import csv


def preprocess():
    """Special version for Streamlit Cloud buffer overflow issue"""

    print("=" * 50)
    print("PREPROCESSOR - STREAMLIT CLOUD SPECIAL VERSION")
    print("=" * 50)

    current_dir = '/mount/src/olympic_data_analyser_new'
    print(f"📁 Working directory: {current_dir}")

    athlete_file = os.path.join(current_dir, 'athlete_events.csv')
    noc_file = os.path.join(current_dir, 'noc_regions.csv')

    print(f"\n🔍 Checking files:")
    print(f"   athlete_events.csv exists: {os.path.exists(athlete_file)}")
    print(f"   noc_regions.csv exists: {os.path.exists(noc_file)}")

    if os.path.exists(athlete_file):
        file_size = os.path.getsize(athlete_file)
        print(f"📊 athlete_events.csv size: {file_size} bytes ({file_size / 1e6:.2f} MB)")

        # METHOD 1: Try reading with csv module first (most reliable)
        print("\n📖 METHOD 1: Reading with csv module...")
        try:
            rows = []
            with open(athlete_file, 'r', encoding='latin1') as f:
                csv_reader = csv.reader(f)
                headers = next(csv_reader)
                print(f"   Headers: {headers[:10]}...")

                count = 0
                for row in csv_reader:
                    rows.append(row)
                    count += 1
                    if count % 50000 == 0:
                        print(f"   Read {count} rows...")

            print(f"✅ Successfully read {count} rows with csv module")

            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=headers)
            print(f"✅ Converted to DataFrame: {df.shape}")

        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
            df = None

        # METHOD 2: Try with chunks but smaller size
        if df is None:
            print("\n📖 METHOD 2: Reading with tiny chunks...")
            try:
                chunks = []
                for chunk in pd.read_csv(athlete_file, encoding='latin1', chunksize=10000,
                                         on_bad_lines='skip', engine='c'):
                    chunks.append(chunk)
                    print(f"   Loaded chunk with {len(chunk)} rows")

                if chunks:
                    df = pd.concat(chunks, ignore_index=True)
                    print(f"✅ Successfully loaded {len(df)} rows with chunks")
            except Exception as e:
                print(f"❌ Method 2 failed: {e}")
                df = None

        # METHOD 3: Try with python engine
        if df is None:
            print("\n📖 METHOD 3: Reading with python engine...")
            try:
                df = pd.read_csv(athlete_file, encoding='latin1', engine='python',
                                 on_bad_lines='skip')
                print(f"✅ Successfully loaded {len(df)} rows with python engine")
            except Exception as e:
                print(f"❌ Method 3 failed: {e}")
                df = None

        # If all methods failed, create sample data
        if df is None:
            print("\n⚠️ All reading methods failed!")
            return create_enhanced_sample_data()

        # Load region data
        region_df = None
        if os.path.exists(noc_file):
            try:
                region_df = pd.read_csv(noc_file, encoding='latin1')
                print(f"✅ Loaded noc_regions.csv: {len(region_df)} rows")
            except:
                print("⚠️ Could not load noc_regions.csv")

        # Process the data
        return process_olympic_data(df, region_df)
    else:
        print("❌ athlete_events.csv not found!")
        return create_enhanced_sample_data()


def process_olympic_data(df, region_df=None):
    """Process the Olympic data"""

    print("\n🔧 Processing Olympic data...")

    # Filter Summer Olympics
    if 'Season' in df.columns:
        df = df[df['Season'] == 'Summer'].copy()
        print(f"✅ Filtered Summer Olympics: {len(df)} rows")

    # Convert Year to int
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

    # Merge with region data
    if region_df is not None and 'NOC' in df.columns:
        df = df.merge(region_df, on='NOC', how='left')
        if 'region' in df.columns:
            df['region'] = df['region'].fillna(df['NOC'])
        else:
            df['region'] = df['NOC']

    # Create medal columns
    if 'Medal' in df.columns:
        df['Gold'] = (df['Medal'] == 'Gold').astype(int)
        df['Silver'] = (df['Medal'] == 'Silver').astype(int)
        df['Bronze'] = (df['Medal'] == 'Bronze').astype(int)
    else:
        df['Gold'] = 0
        df['Silver'] = 0
        df['Bronze'] = 0

    # Remove duplicates
    dup_cols = ['Team', 'NOC', 'Games', 'Year', 'Sport', 'Event', 'Medal']
    existing_cols = [col for col in dup_cols if col in df.columns]
    if existing_cols:
        df = df.drop_duplicates(subset=existing_cols)

    # Final check
    print(f"\n✅ FINAL DATAFRAME: {df.shape}")
    print(f"✅ Countries: {df['region'].nunique() if 'region' in df.columns else 0}")
    print(f"✅ Years: {df['Year'].min()} - {df['Year'].max()}")

    return df


def create_enhanced_sample_data():
    """Create enhanced sample data as last resort"""
    print("\n📊 CREATING ENHANCED SAMPLE DATA")

    # Use more countries for realistic data
    countries = [
        ('USA', 'United States'), ('CHN', 'China'), ('RUS', 'Russia'),
        ('GBR', 'Great Britain'), ('GER', 'Germany'), ('FRA', 'France'),
        ('ITA', 'Italy'), ('AUS', 'Australia'), ('JPN', 'Japan'),
        ('CAN', 'Canada'), ('KOR', 'South Korea'), ('BRA', 'Brazil'),
        ('IND', 'India'), ('KEN', 'Kenya'), ('JAM', 'Jamaica')
    ]

    sports = ['Athletics', 'Swimming', 'Gymnastics', 'Basketball', 'Football',
              'Tennis', 'Boxing', 'Weightlifting', 'Wrestling', 'Judo']

    years = list(range(2000, 2021, 4))

    data = []
    for year in years:
        for sport in sports:
            for event_num in range(1, 4):
                for noc, region in countries:
                    # Random medal assignment
                    import random
                    medal = random.choice(['Gold', 'Silver', 'Bronze', None])
                    if medal:
                        data.append({
                            'Year': year,
                            'Sport': sport,
                            'Event': f"{sport} - Event {event_num}",
                            'NOC': noc,
                            'region': region,
                            'Medal': medal,
                            'Name': f"{region} Athlete",
                            'Season': 'Summer',
                            'Gold': 1 if medal == 'Gold' else 0,
                            'Silver': 1 if medal == 'Silver' else 0,
                            'Bronze': 1 if medal == 'Bronze' else 0
                        })

    df = pd.DataFrame(data)
    print(f"✅ Created {len(df)} rows of sample data")
    print(f"✅ Countries: {df['region'].nunique()}")

    return df