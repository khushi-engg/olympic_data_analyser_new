import pandas as pd

def preprocess():
    # Try UTF-8 first
    df = pd.DataFrame()
    region_df = pd.DataFrame()

    # --- Load athlete_events.csv ---
    try:
        df = pd.read_csv('athlete_events.csv', encoding='utf-8')
    except (UnicodeDecodeError, pd.errors.ParserError):
        try:
            df = pd.read_csv(
                'athlete_events.csv',
                encoding='latin1',
                engine='python',
                on_bad_lines='skip'
            )
        except Exception as e:
            print(f"Failed to read athlete_events.csv: {e}")
            return pd.DataFrame()  # Return empty DataFrame on failure

    # --- Load noc_regions.csv ---
    try:
        region_df = pd.read_csv('noc_regions.csv', encoding='utf-8')
    except (UnicodeDecodeError, pd.errors.ParserError):
        try:
            region_df = pd.read_csv(
                'noc_regions.csv',
                encoding='latin1',
                engine='python',
                on_bad_lines='skip'
            )
        except Exception as e:
            print(f"Failed to read noc_regions.csv: {e}")
            return pd.DataFrame()


    df = df[df['Season'] == 'Summer']
    df = df.merge(region_df, on='NOC', how='left')
    df['region'].fillna('Unknown', inplace=True)
    df = df.drop_duplicates()

    df = pd.concat([df, pd.get_dummies(df['Medal'])], axis=1)

    return df