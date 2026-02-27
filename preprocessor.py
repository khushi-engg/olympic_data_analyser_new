import pandas as pd

def preprocess():
    """
    Reads athlete_events.csv and noc_regions.csv robustly.
    Handles UnicodeDecodeError, ParserError, and missing columns.
    Returns cleaned dataframe ready for analysis.
    """

    df = pd.DataFrame()
    region_df = pd.DataFrame()

    # --- Load athlete_events.csv ---
    for encoding in ['utf-8', 'latin1']:
        try:
            df = pd.read_csv('athlete_events.csv', encoding=encoding, engine='python', on_bad_lines='skip')
            break
        except Exception as e:
            print(f"Failed to read athlete_events.csv with encoding {encoding}: {e}")
            continue

    # --- Load noc_regions.csv ---
    for encoding in ['utf-8', 'latin1']:
        try:
            region_df = pd.read_csv('noc_regions.csv', encoding=encoding, engine='python', on_bad_lines='skip')
            break
        except Exception as e:
            print(f"Failed to read noc_regions.csv with encoding {encoding}: {e}")
            continue

    # --- Check columns before processing ---
    if df.empty or region_df.empty:
        print("One or both CSVs are empty. Returning empty DataFrame.")
        return pd.DataFrame()

    if 'Season' in df.columns:
        df = df[df['Season'] == 'Summer']
    else:
        print("Warning: 'Season' column not found. Skipping season filter.")

    if 'NOC' in df.columns and 'NOC' in region_df.columns:
        df = df.merge(region_df, on='NOC', how='left')
        if 'region' in df.columns:
            df['region'].fillna('Unknown', inplace=True)
    else:
        print("Warning: 'NOC' column missing. Skipping merge.")

    df = df.drop_duplicates()

    if 'Medal' in df.columns:
        df = pd.concat([df, pd.get_dummies(df['Medal'])], axis=1)
        # Ensure medal columns exist
        for medal in ['Gold', 'Silver', 'Bronze']:
            if medal not in df.columns:
                df[medal] = 0
    else:
        print("Warning: 'Medal' column not found. Skipping dummy encoding.")

    return df