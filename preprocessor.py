import pandas as pd

def preprocess():
    df = pd.DataFrame()
    region_df = pd.DataFrame()

    # --- Load athlete_events.csv ---
    for encoding in ['utf-8', 'latin1']:
        try:
            df = pd.read_csv(
                'athlete_events.csv',
                encoding=encoding,
                engine='python',
                on_bad_lines='skip'
            )
            break
        except Exception as e:
            print(f"Failed to read athlete_events.csv with encoding {encoding}: {e}")
            continue

    # --- Load noc_regions.csv ---
    for encoding in ['utf-8', 'latin1']:
        try:
            region_df = pd.read_csv(
                'noc_regions.csv',
                encoding=encoding,
                engine='python',
                on_bad_lines='skip'
            )
            break
        except Exception as e:
            print(f"Failed to read noc_regions.csv with encoding {encoding}: {e}")
            continue

    # --- Check if data was loaded ---
    if df.empty:
        print("athlete_events.csv could not be loaded or is empty.")
        return pd.DataFrame()

    # --- Safely filter 'Season' ---
    if 'Season' in df.columns:
        df = df[df['Season'] == 'Summer']
    else:
        print("Warning: 'Season' column not found. Returning full DataFrame without filtering.")

    # --- Safely merge with regions ---
    if 'NOC' in df.columns and 'NOC' in region_df.columns:
        df = df.merge(region_df, on='NOC', how='left')
        if 'region' in df.columns:
            df['region'] = df['region'].fillna('Unknown')
    else:
        print("Warning: 'NOC' column missing. Skipping merge.")

    df = df.drop_duplicates()

    # --- Safely encode medals ---
    if 'Medal' in df.columns:
        df = pd.concat([df, pd.get_dummies(df['Medal'])], axis=1)
        for medal in ['Gold', 'Silver', 'Bronze']:
            if medal not in df.columns:
                df[medal] = 0
    else:
        print("Warning: 'Medal' column missing. Skipping dummy encoding.")

    return df