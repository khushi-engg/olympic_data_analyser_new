import pandas as pd

def preprocess():
    df = pd.read_csv('athlete_events.csv', encoding='latin1')
    region_df = pd.read_csv('noc_regions.csv', encoding='latin1')

    df = df[df['Season'] == 'Summer']
    df = df.merge(region_df, on='NOC', how='left')
    df['region'].fillna('Unknown', inplace=True)
    df = df.drop_duplicates()
       
    df = pd.concat([df, pd.get_dummies(df['Medal'])], axis=1)

    return df