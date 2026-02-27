import pandas as pd
import os


def preprocess():
    df = pd.DataFrame()
    region_df = pd.DataFrame()

    # Check if files exist
    if not os.path.exists('athlete_events.csv'):
        print("ERROR: athlete_events.csv file not found in current directory")
        print(f"Current directory: {os.getcwd()}")
        print("Files in directory:", os.listdir())
        return pd.DataFrame()

    if not os.path.exists('noc_regions.csv'):
        print("ERROR: noc_regions.csv file not found in current directory")
        return pd.DataFrame()

    # --- Load athlete_events.csv ---
    for encoding in ['utf-8', 'latin1', 'ISO-8859-1']:
        try:
            print(f"Attempting to read athlete_events.csv with encoding: {encoding}")
            df = pd.read_csv(
                'athlete_events.csv',
                encoding=encoding,
                engine='python',
                on_bad_lines='skip'
            )
            print(f"Success! Loaded {len(df)} rows")
            print(f"Columns found: {df.columns.tolist()}")
            break
        except Exception as e:
            print(f"Failed to read athlete_events.csv with encoding {encoding}: {e}")
            continue

    # --- Load noc_regions.csv ---
    for encoding in ['utf-8', 'latin1', 'ISO-8859-1']:
        try:
            print(f"Attempting to read noc_regions.csv with encoding: {encoding}")
            region_df = pd.read_csv(
                'noc_regions.csv',
                encoding=encoding,
                engine='python',
                on_bad_lines='skip'
            )
            print(f"Success! Loaded {len(region_df)} rows")
            print(f"Columns found: {region_df.columns.tolist()}")
            break
        except Exception as e:
            print(f"Failed to read noc_regions.csv with encoding {encoding}: {e}")
            continue

    # --- Check if data was loaded ---
    if df.empty:
        print("ERROR: athlete_events.csv could not be loaded or is empty.")
        return pd.DataFrame()

    # --- Safely filter 'Season' ---
    if 'Season' in df.columns:
        # Check what values are in Season column
        season_values = df['Season'].unique()
        print(f"Season column values: {season_values}")

        # Filter for Summer
        df = df[df['Season'] == 'Summer']
        print(f"After Summer filter: {len(df)} rows remaining")
    else:
        print("WARNING: 'Season' column not found in DataFrame!")
        print(f"Available columns: {df.columns.tolist()}")
        # If it's the Olympic dataset, maybe it's called something else?
        # Try to check first few rows
        print("First few rows of data:")
        print(df.head())
        print("Returning full DataFrame without filtering.")

    # --- Safely merge with regions ---
    if not region_df.empty:
        if 'NOC' in df.columns and 'NOC' in region_df.columns:
            df = df.merge(region_df, on='NOC', how='left')
            if 'region' in df.columns:
                df['region'] = df['region'].fillna('Unknown')
            else:
                print("WARNING: 'region' column not found after merge")
        else:
            print("WARNING: 'NOC' column missing in one of the DataFrames")
            if 'NOC' not in df.columns:
                print("'NOC' not in df.columns")
            if 'NOC' not in region_df.columns:
                print("'NOC' not in region_df.columns")
    else:
        print("WARNING: region_df is empty, skipping merge")

    # Remove duplicates
    initial_len = len(df)
    df = df.drop_duplicates()
    print(f"Removed {initial_len - len(df)} duplicate rows")

    # --- Safely encode medals ---
    if 'Medal' in df.columns:
        medal_dummies = pd.get_dummies(df['Medal'], prefix='', prefix_sep='')
        df = pd.concat([df, medal_dummies], axis=1)

        # Ensure medal columns exist
        for medal in ['Gold', 'Silver', 'Bronze']:
            if medal not in df.columns:
                df[medal] = 0

        print(f"Medal columns created: Gold, Silver, Bronze")
    else:
        print("WARNING: 'Medal' column missing. Creating empty medal columns.")
        df['Gold'] = 0
        df['Silver'] = 0
        df['Bronze'] = 0

    print(f"Final DataFrame shape: {df.shape}")
    print(f"Final columns: {df.columns.tolist()}")

    return df


# Test the function
if __name__ == "__main__":
    result = preprocess()
    if not result.empty:
        print("Preprocessing successful!")
        print(f"DataFrame info:")
        print(result.info())
    else:
        print("Preprocessing failed - empty DataFrame returned")