import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff


# ----------------- MEDAL TALLY ----------------- #
def medal_tally(df):
    """Return medal tally with safe error handling"""
    if df is None or df.empty:
        return pd.DataFrame(columns=['region', 'Gold', 'Silver', 'Bronze', 'total'])

    # Check required columns
    required_cols = ['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal', 'region']
    if not all(col in df.columns for col in required_cols[:8]):  # Check first 8 columns
        print("Warning: Missing required columns for medal tally")
        return pd.DataFrame(columns=['region', 'Gold', 'Silver', 'Bronze', 'total'])

    try:
        temp_df = df.drop_duplicates(
            subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
        )

        # Ensure medal columns exist
        for medal in ['Gold', 'Silver', 'Bronze']:
            if medal not in temp_df.columns:
                temp_df[medal] = 0

        medal_df = (
            temp_df.groupby('region')[['Gold', 'Silver', 'Bronze']]
            .sum()
            .sort_values('Gold', ascending=False)
            .reset_index()
        )
        medal_df['total'] = medal_df['Gold'] + medal_df['Silver'] + medal_df['Bronze']
        return medal_df
    except Exception as e:
        print(f"Error in medal_tally: {e}")
        return pd.DataFrame(columns=['region', 'Gold', 'Silver', 'Bronze', 'total'])


# ----------------- COUNTRY & YEAR LIST ----------------- #
def country_year_list(df):
    """Return years and countries lists with safe fallbacks"""
    # Default values (website won't crash)
    years = ['Overall']
    country = ['Overall']

    if df is None or df.empty:
        print("Warning: Empty DataFrame in country_year_list")
        return years, country

    # Safely get years
    try:
        if 'Year' in df.columns:
            year_values = df['Year'].dropna().unique()
            if len(year_values) > 0:
                years = sorted(year_values.tolist())
                years.insert(0, 'Overall')
    except Exception as e:
        print(f"Error getting years: {e}")

    # Safely get countries
    try:
        if 'region' in df.columns:
            country_values = df['region'].dropna().unique()
            if len(country_values) > 0:
                country = sorted(country_values.tolist())
                country.insert(0, 'Overall')
    except Exception as e:
        print(f"Error getting countries: {e}")

    return years, country


# ----------------- FETCH MEDAL TALLY ----------------- #
def fetch_medal_tally(df, year, country):
    """Fetch medal tally with safe error handling"""
    # Return empty DataFrame if input is invalid
    if df is None or df.empty:
        return pd.DataFrame(columns=['region', 'Gold', 'Silver', 'Bronze', 'total'])

    try:
        # Create a copy to avoid modifying original
        temp_df = df.copy()

        # Remove duplicates if columns exist
        duplicate_cols = ['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
        existing_cols = [col for col in duplicate_cols if col in temp_df.columns]
        if existing_cols:
            temp_df = temp_df.drop_duplicates(subset=existing_cols)

        # Filter by year
        if year != 'Overall' and 'Year' in temp_df.columns:
            try:
                temp_df = temp_df[temp_df['Year'] == int(year)]
            except:
                pass

        # Filter by country
        if country != 'Overall' and 'region' in temp_df.columns:
            temp_df = temp_df[temp_df['region'] == country]

        # Ensure medal columns exist
        for medal in ['Gold', 'Silver', 'Bronze']:
            if medal not in temp_df.columns:
                temp_df[medal] = 0

        # Group based on selection
        if year == 'Overall' and country != 'Overall' and 'Year' in temp_df.columns and 'region' in temp_df.columns:
            x = (
                temp_df.groupby(['region', 'Year'])[['Gold', 'Silver', 'Bronze']]
                .sum()
                .sort_values(['Year', 'Gold'], ascending=[True, False])
                .reset_index()
            )
            if 'region' in x.columns:
                x = x.drop(columns=['region'])
        elif 'region' in temp_df.columns:
            x = (
                temp_df.groupby('region')[['Gold', 'Silver', 'Bronze']]
                .sum()
                .sort_values('Gold', ascending=False)
                .reset_index()
            )
        else:
            x = pd.DataFrame(columns=['region', 'Gold', 'Silver', 'Bronze'])

        # Add total column
        if not x.empty:
            x['total'] = x['Gold'] + x['Silver'] + x['Bronze']
        else:
            x['total'] = 0

        return x
    except Exception as e:
        print(f"Error in fetch_medal_tally: {e}")
        return pd.DataFrame(columns=['region', 'Gold', 'Silver', 'Bronze', 'total'])


# ----------------- DATA OVER TIME ----------------- #
def data_over_time(df, col):
    """Return data over time with safe error handling"""
    if df is None or df.empty or col not in df.columns or 'Year' not in df.columns:
        return pd.DataFrame(columns=['Edition', col])

    try:
        if col == "region":
            temp_df = df.drop_duplicates(['Year', 'region'])
        else:
            temp_df = df.drop_duplicates(['Year', col])

        x = temp_df.groupby('Year')[col].nunique().reset_index()
        x.rename(columns={'Year': 'Edition', col: col}, inplace=True)
        return x
    except Exception as e:
        print(f"Error in data_over_time: {e}")
        return pd.DataFrame(columns=['Edition', col])


# ----------------- EVENTS PER SPORT OVER TIME ----------------- #
def events_per_sport_over_time(df):
    """Return pivot table of events per sport over time with safe handling"""
    if df is None or df.empty:
        return pd.DataFrame()

    required_cols = ['Year', 'Sport', 'Event']
    if not all(col in df.columns for col in required_cols):
        return pd.DataFrame()

    try:
        temp_df = df.drop_duplicates(subset=['Year', 'Sport', 'Event'])
        pivot_df = temp_df.pivot_table(
            index='Sport',
            columns='Year',
            values='Event',
            aggfunc='count'
        ).fillna(0).astype(int)
        return pivot_df
    except Exception as e:
        print(f"Error in events_per_sport_over_time: {e}")
        return pd.DataFrame()


# ----------------- MOST SUCCESSFUL ATHLETES ----------------- #
def most_successful(df, sport):
    """Return most successful athletes with safe handling"""
    if df is None or df.empty:
        return pd.DataFrame(columns=['Name', 'Total Wins', 'Sport', 'region'])

    try:
        temp_df = df.dropna(subset=['Medal']).copy()
        if temp_df.empty:
            return pd.DataFrame(columns=['Name', 'Total Wins', 'Sport', 'region'])

        if sport != 'Overall' and 'Sport' in temp_df.columns:
            temp_df = temp_df[temp_df['Sport'] == sport]

        if temp_df.empty or 'Name' not in temp_df.columns:
            return pd.DataFrame(columns=['Name', 'Total Wins', 'Sport', 'region'])

        athlete_medals = temp_df['Name'].value_counts().reset_index()
        athlete_medals.columns = ['Name', 'Total Wins']
        top_15 = athlete_medals.head(15)

        # Add athlete info if columns exist
        info_cols = ['Name']
        if 'Sport' in temp_df.columns:
            info_cols.append('Sport')
        if 'region' in temp_df.columns:
            info_cols.append('region')

        athlete_info = temp_df[info_cols].drop_duplicates(subset=['Name'])
        final_output = pd.merge(top_15, athlete_info, on='Name', how='left')

        return final_output.sort_values(by='Total Wins', ascending=False).reset_index(drop=True)
    except Exception as e:
        print(f"Error in most_successful: {e}")
        return pd.DataFrame(columns=['Name', 'Total Wins', 'Sport', 'region'])


# ----------------- COUNTRY YEARWISE MEDAL TALLY ----------------- #
def yearwise_medal_tally(df, country):
    """Return year-wise medal tally for a country with safe handling"""
    if df is None or df.empty or 'region' not in df.columns or 'Year' not in df.columns:
        return pd.DataFrame(columns=['Year', 'Medal'])

    try:
        temp_df = df.dropna(subset=['Medal']).copy()
        if temp_df.empty:
            return pd.DataFrame(columns=['Year', 'Medal'])

        # Remove duplicates
        duplicate_cols = ['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
        existing_cols = [col for col in duplicate_cols if col in temp_df.columns]
        if existing_cols:
            temp_df.drop_duplicates(subset=existing_cols, inplace=True)

        country_df = temp_df[temp_df['region'] == country]
        if country_df.empty:
            return pd.DataFrame(columns=['Year', 'Medal'])

        final_df = country_df.groupby('Year').count()['Medal'].reset_index()
        return final_df
    except Exception as e:
        print(f"Error in yearwise_medal_tally: {e}")
        return pd.DataFrame(columns=['Year', 'Medal'])


# ----------------- COUNTRY SPORT HEATMAP ----------------- #
def country_sport_heatmap(df, country):
    """Return heatmap data for country's performance with safe handling"""
    if df is None or df.empty or 'region' not in df.columns:
        return pd.DataFrame()

    try:
        temp_df = df.dropna(subset=['Medal']).copy()
        if temp_df.empty:
            return pd.DataFrame()

        # Remove duplicates
        duplicate_cols = ['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
        existing_cols = [col for col in duplicate_cols if col in temp_df.columns]
        if existing_cols:
            temp_df.drop_duplicates(subset=existing_cols, inplace=True)

        country_df = temp_df[temp_df['region'] == country]
        if country_df.empty or 'Sport' not in country_df.columns or 'Year' not in country_df.columns:
            return pd.DataFrame()

        pivot_df = country_df.pivot_table(
            index='Sport',
            columns='Year',
            values='Medal',
            aggfunc='count'
        ).fillna(0).astype(int)
        return pivot_df
    except Exception as e:
        print(f"Error in country_sport_heatmap: {e}")
        return pd.DataFrame()


# ----------------- MOST SUCCESSFUL ATHLETES BY COUNTRY ----------------- #
def most_successful2(df, country):
    """Return most successful athletes by country with safe handling"""
    if df is None or df.empty:
        return pd.DataFrame(columns=['Name', 'Total Wins', 'Sport'])

    try:
        temp_df = df.dropna(subset=['Medal']).copy()
        if temp_df.empty:
            return pd.DataFrame(columns=['Name', 'Total Wins', 'Sport'])

        if country != 'Overall' and 'region' in temp_df.columns:
            temp_df = temp_df[temp_df['region'] == country]

        if temp_df.empty or 'Name' not in temp_df.columns:
            return pd.DataFrame(columns=['Name', 'Total Wins', 'Sport'])

        athlete_medals = temp_df['Name'].value_counts().reset_index()
        athlete_medals.columns = ['Name', 'Total Wins']
        top_15 = athlete_medals.head(15)

        # Add sport info if available
        if 'Sport' in temp_df.columns:
            athlete_info = temp_df[['Name', 'Sport']].drop_duplicates(subset=['Name'])
            final_output = pd.merge(top_15, athlete_info, on='Name', how='left')
        else:
            final_output = top_15

        return final_output.sort_values(by='Total Wins', ascending=False).reset_index(drop=True)
    except Exception as e:
        print(f"Error in most_successful2: {e}")
        return pd.DataFrame(columns=['Name', 'Total Wins', 'Sport'])


# ----------------- AGE DISTRIBUTION ----------------- #
def age_distribution(df):
    """Return age distribution plot with safe handling"""
    if df is None or df.empty or 'Age' not in df.columns or 'Medal' not in df.columns:
        # Return empty figure with message
        fig = px.line(title="No age data available")
        fig.update_layout(showlegend=False)
        return fig

    try:
        athlete_df = df.drop_duplicates(subset=['Name', 'region'])

        x_all = athlete_df['Age'].dropna()
        x_gold = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
        x_silver = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
        x_bronze = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

        hist_data = [x_all, x_gold, x_silver, x_bronze]
        group_labels = ['All Athletes', 'Gold', 'Silver', 'Bronze']
        colors = ['#B0C4DE', '#FFD580', '#C1E1C1', '#FFB6C1']

        fig = ff.create_distplot(hist_data, group_labels, bin_size=2, show_hist=False, show_rug=False, colors=colors)
        fig.update_layout(title_text='Age Distribution of Olympic Medalists vs All Athletes',
                          template='plotly_white', xaxis_title='Age', yaxis_title='Density',
                          legend_title='Category', font=dict(size=12))
        return fig
    except Exception as e:
        print(f"Error in age_distribution: {e}")
        fig = px.line(title="Error loading age distribution")
        fig.update_layout(showlegend=False)
        return fig


# ----------------- GOLD AGE DISTRIBUTION BY SPORT ----------------- #
def gold_age_distribution_by_sport(df, famous_sports):
    """Return gold medalist age distribution by sport with safe handling"""
    if df is None or df.empty or not famous_sports:
        fig = px.line(title="No gold medal age data available")
        fig.update_layout(showlegend=False)
        return fig

    try:
        athlete_df = df.drop_duplicates(subset=['Name', 'region', 'Sport', 'Age', 'Medal'])
        hist_data = []
        group_labels = []

        for sport in famous_sports:
            temp_df = athlete_df[athlete_df['Sport'] == sport]
            gold_ages = temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna()
            if not gold_ages.empty:
                hist_data.append(gold_ages)
                group_labels.append(sport)

        if not hist_data:
            fig = px.line(title="No gold medal age data available for selected sports")
            fig.update_layout(showlegend=False)
            return fig

        colors = ['#FFD580', '#C1E1C1', '#FFB6C1', '#B0C4DE', '#A0E7E5', '#FFE0AC', '#D7BAFF', '#FFC2E2']
        fig = ff.create_distplot(hist_data, group_labels, show_hist=False, show_rug=False,
                                 colors=colors[:len(group_labels)])
        fig.update_layout(title_text='Age Distribution of Gold Medalists by Sport',
                          template='plotly_white', xaxis_title='Age', yaxis_title='Density',
                          legend_title='Sport', font=dict(size=12))
        return fig
    except Exception as e:
        print(f"Error in gold_age_distribution_by_sport: {e}")
        fig = px.line(title="Error loading gold medal age distribution")
        fig.update_layout(showlegend=False)
        return fig


# ----------------- HEIGHT VS WEIGHT SCATTER ----------------- #
def height_weight_scatter(df, sport):
    """Return height vs weight scatter plot with safe handling"""
    if df is None or df.empty or not sport:
        fig = px.scatter(title="No data available")
        fig.update_layout(showlegend=False)
        return fig

    try:
        athlete_df = df.drop_duplicates(subset=['Name', 'region', 'Sport', 'Height', 'Weight', 'Medal']).copy()
        athlete_df['Medal'] = athlete_df['Medal'].fillna('No Medal')

        temp_df = athlete_df[athlete_df['Sport'] == sport]
        if temp_df.empty:
            fig = px.scatter(title=f"No height/weight data available for {sport}")
            fig.update_layout(showlegend=False)
            return fig

        fig = px.scatter(temp_df, x='Weight', y='Height', color='Medal',
                         hover_data=['Name', 'region'],
                         color_discrete_map={'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32',
                                             'No Medal': '#A9A9A9'},
                         title=f"Height vs Weight of Athletes in {sport}",
                         template='plotly_white', width=800, height=600)
        fig.update_layout(xaxis_title='Weight (kg)', yaxis_title='Height (cm)', legend_title='Medal Type')
        return fig
    except Exception as e:
        print(f"Error in height_weight_scatter: {e}")
        fig = px.scatter(title=f"Error loading data for {sport}")
        fig.update_layout(showlegend=False)
        return fig


# ----------------- MALE VS FEMALE PARTICIPATION ----------------- #
def male_vs_female_participation(df):
    """Return male vs female participation plot with safe handling"""
    if df is None or df.empty or 'Sex' not in df.columns or 'Year' not in df.columns:
        fig = px.line(title="No participation data available")
        fig.update_layout(showlegend=False)
        return fig

    try:
        athlete_df = df.drop_duplicates(subset=['Name', 'Year'])

        men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
        women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

        final = men.merge(women, on='Year', how='outer').fillna(0)
        final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)

        fig = px.line(final, x='Year', y=['Male', 'Female'],
                      labels={'value': 'Number of Athletes', 'variable': 'Gender'},
                      markers=True, line_shape='spline',
                      color_discrete_sequence=['#1f77b4', '#ff7f0e'])
        fig.update_layout(template='plotly_white', xaxis_title='Year',
                          yaxis_title='Number of Athletes', height=500,
                          legend_title='Gender', margin=dict(l=40, r=40, t=50, b=40))
        return fig
    except Exception as e:
        print(f"Error in male_vs_female_participation: {e}")
        fig = px.line(title="Error loading participation data")
        fig.update_layout(showlegend=False)
        return fig


# ----------------- MALE VS FEMALE PARTICIPATION BY SPORT ----------------- #
def male_vs_female_participation_sport(df, sport):
    """Return male vs female participation by sport with safe handling"""
    if df is None or df.empty or not sport:
        fig = px.line(title="No data available")
        fig.update_layout(showlegend=False)
        return fig

    try:
        athlete_df = df[df['Sport'] == sport].drop_duplicates(subset=['Name', 'Year'])
        if athlete_df.empty:
            fig = px.line(title=f"No participation data available for {sport}")
            fig.update_layout(showlegend=False)
            return fig

        men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
        women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

        final = men.merge(women, on='Year', how='outer').fillna(0)
        final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)

        fig = px.line(final, x='Year', y=['Male', 'Female'],
                      labels={'value': 'Number of Athletes', 'variable': 'Gender'},
                      markers=True, line_shape='spline',
                      color_discrete_sequence=['#1f77b4', '#ff7f0e'])
        fig.update_layout(template='plotly_white', xaxis_title='Year',
                          yaxis_title='Number of Athletes', height=500,
                          legend_title='Gender', margin=dict(l=40, r=40, t=50, b=40))
        return fig
    except Exception as e:
        print(f"Error in male_vs_female_participation_sport: {e}")
        fig = px.line(title=f"Error loading participation data for {sport}")
        fig.update_layout(showlegend=False)
        return fig