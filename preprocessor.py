import pandas as pd

def preprocess():
       try:
        df = pd.read_csv('athlete_events.csv', encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(
            'athlete_events.csv',
            encoding='latin1',
            encoding_errors='ignore'
        )

    try:
        region_df = pd.read_csv('noc_regions.csv', encoding='utf-8')
    except UnicodeDecodeError:
        region_df = pd.read_csv(
            'noc_regions.csv',
            encoding='latin1',
            encoding_errors='ignore'
        )


    df = df[df['Season'] == 'Summer']
    df = df.merge(region_df, on='NOC', how='left')
    df['region'].fillna('Unknown', inplace=True)
    df = df.drop_duplicates()

    df = pd.concat([df, pd.get_dummies(df['Medal'])], axis=1)


    return df
