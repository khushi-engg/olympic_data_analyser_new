import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

# ----------------- MEDAL TALLY ----------------- #
def medal_tally(df):
    temp_df = df.drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )
    medal_df = (
        temp_df.groupby('region')[['Gold', 'Silver', 'Bronze']]
        .sum()
        .sort_values('Gold', ascending=False)
        .reset_index()
    )
    medal_df['total'] = medal_df['Gold'] + medal_df['Silver'] + medal_df['Bronze']
    return medal_df

# ----------------- COUNTRY & YEAR LIST ----------------- #
def country_year_list(df):
    years = sorted(df['Year'].dropna().unique().tolist())
    years.insert(0, 'Overall')
    country = sorted(np.unique(df['region'].dropna().values).tolist())
    country.insert(0, 'Overall')
    return years, country

# ----------------- FETCH MEDAL TALLY ----------------- #
def fetch_medal_tally(df, year, country):
    temp_df = df.drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )
    if year != 'Overall':
        temp_df = temp_df[temp_df['Year'] == int(year)]
    if country != 'Overall':
        temp_df = temp_df[temp_df['region'] == country]
    for col in ['Gold', 'Silver', 'Bronze']:
        if col not in temp_df.columns:
            temp_df[col] = 0
    if year == 'Overall' and country != 'Overall':
        x = (
            temp_df.groupby(['region','Year'])[['Gold','Silver','Bronze']]
            .sum()
            .sort_values(['Year','Gold'], ascending=[True, False])
            .reset_index()
        )
        x = x.drop(columns=['region'])
    else:
        x = (
            temp_df.groupby('region')[['Gold','Silver','Bronze']]
            .sum()
            .sort_values('Gold', ascending=False)
            .reset_index()
        )
    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']
    return x

# ----------------- DATA OVER TIME ----------------- #
def data_over_time(df, col):
    if col == "region":
        temp_df = df.drop_duplicates(['Year', 'region'])
    else:
        temp_df = df.drop_duplicates(['Year', col])
    x = temp_df.groupby('Year')[col].nunique().reset_index()
    x.rename(columns={'Year':'Edition', col:col}, inplace=True)
    return x

# ----------------- EVENTS PER SPORT OVER TIME ----------------- #
def events_per_sport_over_time(df):
    temp_df = df.drop_duplicates(subset=['Year','Sport','Event'])
    pivot_df = temp_df.pivot_table(
        index='Sport',
        columns='Year',
        values='Event',
        aggfunc='count'
    ).fillna(0).astype(int)
    return pivot_df

# ----------------- MOST SUCCESSFUL ATHLETES ----------------- #
def most_successful(df, sport):
    temp_df = df.dropna(subset=['Medal']).copy()
    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]
    athlete_medals = temp_df['Name'].value_counts().reset_index()
    athlete_medals.columns = ['Name', 'Total Wins']
    top_15 = athlete_medals.head(15)
    athlete_info = temp_df[['Name','Sport','region']].drop_duplicates(subset=['Name','Sport','region'])
    final_output = pd.merge(top_15, athlete_info, on='Name', how='left')
    return final_output.sort_values(by='Total Wins', ascending=False).reset_index(drop=True)

# ----------------- COUNTRY YEARWISE MEDAL TALLY ----------------- #
def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=['Medal']).copy()
    temp_df.drop_duplicates(subset=['Team','NOC','Games','Year','City','Sport','Event','Medal'], inplace=True)
    country_df = temp_df[temp_df['region'] == country]
    final_df = country_df.groupby('Year').count()['Medal'].reset_index()
    return final_df

# ----------------- COUNTRY SPORT HEATMAP ----------------- #
def country_sport_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal']).copy()
    temp_df.drop_duplicates(subset=['Team','NOC','Games','Year','City','Sport','Event','Medal'], inplace=True)
    country_df = temp_df[temp_df['region'] == country]
    if country_df.empty:
        return pd.DataFrame()
    pivot_df = country_df.pivot_table(
        index='Sport',
        columns='Year',
        values='Medal',
        aggfunc='count'
    ).fillna(0).astype(int)
    return pivot_df

# ----------------- MOST SUCCESSFUL ATHLETES BY COUNTRY ----------------- #
def most_successful2(df, country):
    temp_df = df.dropna(subset=['Medal']).copy()
    if country != 'Overall':
        temp_df = temp_df[temp_df['region'] == country]
    athlete_medals = temp_df['Name'].value_counts().reset_index()
    athlete_medals.columns = ['Name', 'Total Wins']
    top_15 = athlete_medals.head(15)
    athlete_info = temp_df[['Name','Sport']].drop_duplicates(subset=['Name','Sport'])
    final_output = pd.merge(top_15, athlete_info, on='Name', how='left')
    return final_output.sort_values(by='Total Wins', ascending=False).reset_index(drop=True)

# ----------------- AGE DISTRIBUTION ----------------- #
def age_distribution(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    x_all = athlete_df['Age'].dropna()
    x_gold = athlete_df[athlete_df['Medal']=='Gold']['Age'].dropna()
    x_silver = athlete_df[athlete_df['Medal']=='Silver']['Age'].dropna()
    x_bronze = athlete_df[athlete_df['Medal']=='Bronze']['Age'].dropna()
    hist_data = [x_all, x_gold, x_silver, x_bronze]
    group_labels = ['All Athletes','Gold','Silver','Bronze']
    colors = ['#B0C4DE','#FFD580','#C1E1C1','#FFB6C1']
    fig = ff.create_distplot(hist_data, group_labels, bin_size=2, show_hist=False, show_rug=False, colors=colors)
    fig.update_layout(title_text='Age Distribution of Olympic Medalists vs All Athletes',
                      template='plotly_white', xaxis_title='Age', yaxis_title='Density', legend_title='Category', font=dict(size=12))
    return fig

# ----------------- GOLD AGE DISTRIBUTION BY SPORT ----------------- #
def gold_age_distribution_by_sport(df, famous_sports):
    athlete_df = df.drop_duplicates(subset=['Name','region','Sport','Age','Medal'])
    hist_data = []
    group_labels = []
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport']==sport]
        gold_ages = temp_df[temp_df['Medal']=='Gold']['Age'].dropna()
        if not gold_ages.empty:
            hist_data.append(gold_ages)
            group_labels.append(sport)
    if not hist_data:
        return None
    colors = ['#FFD580','#C1E1C1','#FFB6C1','#B0C4DE','#A0E7E5','#FFE0AC','#D7BAFF','#FFC2E2']
    fig = ff.create_distplot(hist_data, group_labels, show_hist=False, show_rug=False, colors=colors[:len(group_labels)])
    fig.update_layout(title_text='Age Distribution of Gold Medalists by Sport',
                      template='plotly_white', xaxis_title='Age', yaxis_title='Density', legend_title='Sport', font=dict(size=12))
    return fig

# ----------------- HEIGHT VS WEIGHT SCATTER ----------------- #
def height_weight_scatter(df, sport):
    athlete_df = df.drop_duplicates(subset=['Name','region','Sport','Height','Weight','Medal']).copy()
    athlete_df['Medal'] = athlete_df['Medal'].fillna('No Medal')
    temp_df = athlete_df[athlete_df['Sport']==sport]
    if temp_df.empty:
        return None
    fig = px.scatter(temp_df, x='Weight', y='Height', color='Medal',
                     hover_data=['Name','region'],
                     color_discrete_map={'Gold':'#FFD700','Silver':'#C0C0C0','Bronze':'#CD7F32','No Medal':'#A9A9A9'},
                     title=f"Height vs Weight of Athletes in {sport}", template='plotly_white', width=800, height=600)
    fig.update_layout(xaxis_title='Weight (kg)', yaxis_title='Height (cm)', legend_title='Medal Type')
    return fig

# ----------------- MALE VS FEMALE PARTICIPATION ----------------- #
def male_vs_female_participation(df):
    athlete_df = df.drop_duplicates(subset=['Name','Year'])
    men = athlete_df[athlete_df['Sex']=='M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex']=='F'].groupby('Year').count()['Name'].reset_index()
    final = men.merge(women, on='Year', how='outer').fillna(0)
    final.rename(columns={'Name_x':'Male','Name_y':'Female'}, inplace=True)
    fig = px.line(final, x='Year', y=['Male','Female'], labels={'value':'Number of Athletes','variable':'Gender'},
                  markers=True, line_shape='spline', color_discrete_sequence=['#1f77b4','#ff7f0e'])
    fig.update_layout(template='plotly_white', xaxis_title='Year', yaxis_title='Number of Athletes', height=500,
                      legend_title='Gender', margin=dict(l=40,r=40,t=50,b=40))
    return fig

# ----------------- MALE VS FEMALE PARTICIPATION BY SPORT ----------------- #
def male_vs_female_participation_sport(df, sport):
    athlete_df = df[df['Sport']==sport].drop_duplicates(subset=['Name','Year'])
    if athlete_df.empty:
        return None
    men = athlete_df[athlete_df['Sex']=='M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex']=='F'].groupby('Year').count()['Name'].reset_index()
    final = men.merge(women, on='Year', how='outer').fillna(0)
    final.rename(columns={'Name_x':'Male','Name_y':'Female'}, inplace=True)
    fig = px.line(final, x='Year', y=['Male','Female'], labels={'value':'Number of Athletes','variable':'Gender'},
                  markers=True, line_shape='spline', color_discrete_sequence=['#1f77b4','#ff7f0e'])
    fig.update_layout(template='plotly_white', xaxis_title='Year', yaxis_title='Number of Athletes', height=500,
                      legend_title='Gender', margin=dict(l=40,r=40,t=50,b=40))
    return fig