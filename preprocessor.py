import pandas as pd

def preprocess():
    # Try UTF-8 first
    df = pd.read_csv(
        'athlete_events.csv',
        encoding='utf-8',  # try utf-8 first
        engine='python',  # use python engine to avoid buffer overflow
        on_bad_lines='skip'  # skip malformed lines
    )

    # Read noc_regions.csv robustly
    region_df = pd.read_csv(
        'noc_regions.csv',
        encoding='utf-8',
        engine='python',
        on_bad_lines='skip'
    )


    df = df[df['Season'] == 'Summer']
    df = df.merge(region_df, on='NOC', how='left')
    df['region'].fillna('Unknown', inplace=True)
    df = df.drop_duplicates()

    df = pd.concat([df, pd.get_dummies(df['Medal'])], axis=1)

    return df