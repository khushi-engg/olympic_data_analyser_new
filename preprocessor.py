# preprocessor.py - HYBRID VERSION (REAL DATA IF AVAILABLE, SAMPLE IF NOT)

import pandas as pd
import os
import numpy as np

def preprocess():
    """Load REAL Olympic data if available, otherwise use SAMPLE data"""

    print("=" * 50)
    print("PREPROCESSOR - HYBRID MODE")
    print("=" * 50)

    # Get current directory
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")

    # Check if real data exists
    athlete_path = os.path.join(current_dir, 'athlete_events.csv')
    noc_path = os.path.join(current_dir, 'noc_regions.csv')

    real_data_available = os.path.exists(athlete_path) and os.path.exists(noc_path)

    if real_data_available:
        print("✅ REAL DATA FILES FOUND!")
        print(f"   athlete_events.csv size: {os.path.getsize(athlete_path) / 1e6:.2f} MB")
        print(f"   noc_regions.csv size: {os.path.getsize(noc_path) / 1e6:.2f} MB")

        # Try to load real data
        df = load_real_data(athlete_path, noc_path)

        if df is not None and not df.empty:
            print("\n✅ SUCCESSFULLY LOADED REAL OLYMPIC DATA!")
            return df
        else:
            print("\n⚠️ Failed to load real data, falling back to sample data...")
            return create_comprehensive_sample_data()
    else:
        print("❌ REAL DATA FILES NOT FOUND!")
        print("   Expected files:")
        print(f"   - {athlete_path}")
        print(f"   - {noc_path}")
        print("\n📋 Creating comprehensive sample data instead...")
        return create_comprehensive_sample_data()


def load_real_data(athlete_path, noc_path):
    """Attempt to load real Olympic data"""
    try:
        print("\n📖 Loading real Olympic data...")

        # Load in chunks to avoid memory issues
        chunks = []
        chunk_count = 0
        for chunk in pd.read_csv(athlete_path, encoding='latin1', chunksize=100000, on_bad_lines='skip'):
            chunk_count += 1
            print(f"   Loaded chunk {chunk_count}: {len(chunk)} rows")
            chunks.append(chunk)

        if not chunks:
            return None

        df = pd.concat(chunks, ignore_index=True)
        print(f"✅ Total rows loaded: {len(df):,}")

        # Load region data
        region_df = pd.read_csv(noc_path, encoding='latin1')
        print(f"✅ Loaded region data: {len(region_df)} countries")

        # Process the data
        return process_dataframe(df, region_df)

    except Exception as e:
        print(f"❌ Error loading real data: {e}")
        return None


def process_dataframe(df, region_df=None):
    """Process the dataframe with all necessary transformations"""

    print("\n🔧 Processing data...")

    # Filter for Summer Olympics
    if 'Season' in df.columns:
        original_count = len(df)
        df = df[df['Season'] == 'Summer'].copy()
        print(f"✅ Filtered Summer Olympics: {original_count:,} → {len(df):,} rows")

    # Merge with region data
    if region_df is not None and 'NOC' in df.columns and 'NOC' in region_df.columns:
        df = df.merge(region_df[['NOC', 'region']], on='NOC', how='left')
        df['region'] = df['region'].fillna('Unknown')
        print(f"✅ Merged with region data")
    else:
        df['region'] = df['NOC'] if 'NOC' in df.columns else 'Unknown'

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

    # Ensure required columns exist
    for col in ['Year', 'region', 'Sport', 'Name', 'City']:
        if col not in df.columns:
            if col == 'Year':
                df[col] = 2016
            elif col == 'City':
                df[col] = 'Unknown'
            else:
                df[col] = 'Unknown'

    # Remove duplicates (optimized)
    dup_cols = ['Team', 'NOC', 'Games', 'Year', 'Sport', 'Event', 'Medal']
    existing_cols = [col for col in dup_cols if col in df.columns]
    if existing_cols:
        original_count = len(df)
        df = df.drop_duplicates(subset=existing_cols)
        print(f"✅ Removed {original_count - len(df):,} duplicates")

    return df


def create_comprehensive_sample_data():
    """Create comprehensive sample data with many countries and real statistics"""
    print("\n📊 CREATING COMPREHENSIVE SAMPLE DATA")

    # Real Olympic countries (top 30 medal-winning nations)
    countries_data = [
        ('USA', 'United States'),
        ('CHN', 'China'),
        ('RUS', 'Russia'),
        ('GBR', 'Great Britain'),
        ('GER', 'Germany'),
        ('FRA', 'France'),
        ('ITA', 'Italy'),
        ('AUS', 'Australia'),
        ('JPN', 'Japan'),
        ('CAN', 'Canada'),
        ('KOR', 'South Korea'),
        ('NED', 'Netherlands'),
        ('BRA', 'Brazil'),
        ('ESP', 'Spain'),
        ('HUN', 'Hungary'),
        ('SWE', 'Sweden'),
        ('NOR', 'Norway'),
        ('DEN', 'Denmark'),
        ('POL', 'Poland'),
        ('CUB', 'Cuba'),
        ('NZL', 'New Zealand'),
        ('JAM', 'Jamaica'),
        ('KEN', 'Kenya'),
        ('ETH', 'Ethiopia'),
        ('ROU', 'Romania'),
        ('BUL', 'Bulgaria'),
        ('GRE', 'Greece'),
        ('ARG', 'Argentina'),
        ('RSA', 'South Africa'),
        ('MEX', 'Mexico'),
        ('IND', 'India'),
    ]

    # Real Olympic sports
    sports = [
        'Athletics', 'Swimming', 'Gymnastics', 'Basketball', 'Football',
        'Tennis', 'Boxing', 'Weightlifting', 'Wrestling', 'Judo',
        'Rowing', 'Canoeing', 'Cycling', 'Equestrian', 'Fencing',
        'Handball', 'Hockey', 'Sailing', 'Shooting', 'Table Tennis',
        'Taekwondo', 'Triathlon', 'Volleyball', 'Beach Volleyball',
        'Archery', 'Badminton', 'Golf', 'Rugby', 'Softball', 'Baseball'
    ]

    # Realistic medal distribution (based on historical data)
    years = list(range(1980, 2021, 4))

    data = []

    for year in years:
        # Host city based on year
        host_cities = {
            1980: 'Moscow', 1984: 'Los Angeles', 1988: 'Seoul',
            1992: 'Barcelona', 1996: 'Atlanta', 2000: 'Sydney',
            2004: 'Athens', 2008: 'Beijing', 2012: 'London',
            2016: 'Rio', 2020: 'Tokyo'
        }
        city = host_cities.get(year, 'Unknown')

        for sport in sports:
            # Number of events per sport (1-5)
            num_events = np.random.randint(1, 6)

            for event_num in range(1, num_events + 1):
                event_name = f"{sport} - Event {event_num}"

                # Generate medals for this event
                for medal_type in ['Gold', 'Silver', 'Bronze']:
                    # Random country (weighted by historical performance)
                    country_idx = np.random.choice(len(countries_data), p=[
                        0.15, 0.12, 0.10, 0.08, 0.07, 0.05, 0.05, 0.04, 0.04, 0.03,
                        0.03, 0.02, 0.02, 0.02, 0.02, 0.01, 0.01, 0.01, 0.01, 0.01,
                        0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01,
                        0.01
                    ])

                    noc, region = countries_data[country_idx]

                    # Create athlete name
                    athlete_name = f"{region} Athlete {np.random.randint(1, 999)}"

                    data.append({
                        'Year': year,
                        'City': city,
                        'Sport': sport,
                        'Event': event_name,
                        'NOC': noc,
                        'region': region,
                        'Medal': medal_type,
                        'Name': athlete_name,
                        'Season': 'Summer',
                        'Gold': 1 if medal_type == 'Gold' else 0,
                        'Silver': 1 if medal_type == 'Silver' else 0,
                        'Bronze': 1 if medal_type == 'Bronze' else 0,
                        'Age': np.random.randint(18, 40),
                        'Height': np.random.randint(150, 210),
                        'Weight': np.random.randint(50, 120)
                    })

    df = pd.DataFrame(data)
    print(f"✅ Created {len(df):,} rows of sample data")
    print(f"✅ Countries: {df['region'].nunique()}")
    print(f"✅ Sports: {df['Sport'].nunique()}")
    print(f"✅ Years: {df['Year'].min()} - {df['Year'].max()}")

    return df