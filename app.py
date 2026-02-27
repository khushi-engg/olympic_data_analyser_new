import streamlit as st
import pandas as pd
import preprocessor
import helper
import plotly.express as px

# ----------------- PAGE CONFIG ----------------- #
st.set_page_config(page_title="Olympics Data Analysis", layout="wide")

# ----------------- LOAD DATA ----------------- #
@st.cache_data
def load_data():
    return preprocessor.preprocess()

df = load_data()

# ----------------- MAIN TITLE ----------------- #
st.markdown("<h1 style='text-align: center;'>Olympics Data Analysis</h1>", unsafe_allow_html=True)

# ----------------- SIDEBAR MENU ----------------- #
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/5/5c/Olympic_rings_without_rims.svg",
    width=200
)
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
)

# ----------------- MEDAL TALLY ----------------- #
if user_menu == 'Medal Tally':
    st.sidebar.title('Olympics Analysis')
    st.markdown("<h2 style='text-align: center;'>🏅 Medal Tally Analysis</h2>", unsafe_allow_html=True)

    with st.expander("🔎 Show Raw Data"):
        st.dataframe(df, use_container_width=True)

    st.sidebar.header("Filter Options")
    years, country = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    # Dynamic subtitle
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.subheader("🏅 Overall Medal Tally")
    elif selected_year != 'Overall' and selected_country == 'Overall':
        st.subheader(f"🏅 Medal Tally in {selected_year}")
    elif selected_year == 'Overall' and selected_country != 'Overall':
        st.subheader(f"🏅 Overall Performance of {selected_country}")
    else:
        st.subheader(f"🏅 {selected_country} Performance in {selected_year} Olympics")

    st.dataframe(medal_tally, use_container_width=True)

# ----------------- OVERALL ANALYSIS ----------------- #
elif user_menu == 'Overall Analysis':
    st.markdown("<h2 style='text-align: center;'>📊 Overall Analysis</h2>", unsafe_allow_html=True)

    editions = df['Year'].nunique() - 1
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Editions", editions)
    col2.metric("Hosts", cities)
    col3.metric("Sports", sports)

    col1, col2, col3 = st.columns(3)
    col1.metric("Events", events)
    col2.metric("Nations", nations)
    col3.metric("Athletes", athletes)

    # Nations over time
    nations_over_time = helper.data_over_time(df, "region")
    fig = px.line(nations_over_time, x='Edition', y='region', markers=True, line_shape='spline',
                  color_discrete_sequence=['#89CFF0'])
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=450)
    fig.update_traces(line=dict(width=3))
    st.title("Participating Nations Over the Years")
    st.plotly_chart(fig, use_container_width=True)

    # Events over time
    events_over_time = helper.data_over_time(df, "Event")
    fig = px.line(events_over_time, x='Edition', y='Event', markers=True, line_shape='spline',
                  color_discrete_sequence=['#A3C1AD'])
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=450)
    fig.update_traces(line=dict(width=3))
    st.title("Events Over the Years")
    st.plotly_chart(fig, use_container_width=True)

    # Athletes over time
    athletes_over_time = helper.data_over_time(df, "Name")
    fig = px.line(athletes_over_time, x='Edition', y='Name', markers=True, line_shape='spline',
                  color_discrete_sequence=['#FFD580'])
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=450)
    fig.update_traces(line=dict(width=3))
    st.title("Athletes Over the Years")
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap: Events per sport
    heatmap_data = helper.events_per_sport_over_time(df)
    fig = px.imshow(
        heatmap_data,
        labels=dict(x="Year", y="Sport", color="Number of Events"),
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Viridis"
    )
    fig.update_layout(title="Number of Events per Sport Over the Years", xaxis_title="Year", yaxis_title="Sport", height=800)
    st.plotly_chart(fig, use_container_width=True)

    # Most successful athletes
    st.markdown("<h3 style='text-align: center;'>🏅 Most Successful Athletes</h3>", unsafe_allow_html=True)
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox("Select Sport", sport_list, key="overall_athletes")
    top_athletes = helper.most_successful(df, selected_sport)
    st.dataframe(top_athletes[['Name', 'Total Wins', 'Sport', 'region']].reset_index(drop=True))

    fig = px.bar(
        top_athletes.head(10),
        x='Total Wins',
        y='Name',
        color='Sport',
        orientation='h',
        text='Total Wins',
        color_discrete_sequence=[
            '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF',
            '#D7BAFF', '#FFC2E2', '#BFFCC6', '#FFE0AC', '#A0E7E5'
        ]
    )
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=600, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

# ----------------- COUNTRY-WISE ANALYSIS ----------------- #
elif user_menu == 'Country-wise Analysis':
    st.markdown("<h2 style='text-align: center;'>🏅 Country-wise Yearwise Medal Tally</h2>", unsafe_allow_html=True)

    # ----------------- Sidebar country selection ----------------- #
    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()
    selected_country = st.sidebar.selectbox(
        "Select a Country",
        country_list,
        index=country_list.index('United States') if 'United States' in country_list else 0
    )

    # ----------------- Yearwise medal tally table & line ----------------- #
    country_medal_df = helper.yearwise_medal_tally(df, selected_country)

    if country_medal_df.empty:
        st.warning(f"No medals found for {selected_country}.")
    else:
        # Rename column for consistent usage
        country_medal_df = country_medal_df.rename(columns={'Medal': 'Total Medals'})

        # Display table
        st.dataframe(country_medal_df)

        # Create line chart using the renamed column
        fig = px.line(
            country_medal_df,
            x='Year',
            y='Total Medals',  # <-- use renamed column
            markers=True,
            line_shape='spline',
            color_discrete_sequence=['#FFB347']
        )
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=20, r=20, t=40, b=20),
            height=450,
            xaxis_title="Year",
            yaxis_title="Total Medals"
        )
        fig.update_traces(line=dict(width=3))
        st.plotly_chart(fig, use_container_width=True)

    # ----------------- Country-specific sport heatmap ----------------- #
    st.markdown(f"<h3 style='text-align: center;'>🏆 Medals per Sport Heatmap for {selected_country}</h3>",
                unsafe_allow_html=True)

    heatmap_data = helper.country_sport_heatmap(df, selected_country)
    if heatmap_data.empty:
        st.warning(f"No medals found for {selected_country} to display heatmap.")
    else:
        fig = px.imshow(
            heatmap_data,
            labels=dict(x="Year", y="Sport", color="Number of Medals"),
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(
            title=f"Medals per Sport Over the Years - {selected_country}",
            xaxis_title="Year",
            yaxis_title="Sport",
            template="plotly_dark",
            height=700,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    # ----------------- Most Successful Athletes ----------------- #
    st.markdown(f"<h3 style='text-align: center;'>🏅 Most Successful Athletes - {selected_country}</h3>", unsafe_allow_html=True)
    top_athletes = helper.most_successful2(df, selected_country)

    if top_athletes.empty:
        st.warning(f"No athlete data found for {selected_country}.")
    else:
        # Show as table
        st.dataframe(top_athletes[['Name','Total Wins','Sport']].reset_index(drop=True))

        # Horizontal bar chart
        fig = px.bar(
            top_athletes.head(10),
            x='Total Wins',
            y='Name',
            color='Sport',
            orientation='h',
            text='Total Wins',
            color_discrete_sequence=[
                '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF',
                '#D7BAFF', '#FFC2E2', '#BFFCC6', '#FFE0AC', '#A0E7E5'
            ]
        )
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=20, r=20, t=40, b=20),
            height=600,
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig, use_container_width=True)

# ----------------- ATHLETE-WISE ANALYSIS ----------------- #
elif user_menu == 'Athlete-wise Analysis':
    st.markdown("<h2 style='text-align: center;'>🏃 Athlete Analysis</h2>", unsafe_allow_html=True)

    st.markdown("### Age Distribution of Athletes and Medalists")

    # Get the figure from helper
    fig = helper.age_distribution(df)

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    famous_sports = st.sidebar.multiselect(
        "Select Sports for Gold Medalist Age Distribution",
        options=df['Sport'].unique().tolist(),
        default=['Athletics', 'Swimming', 'Gymnastics', 'Rowing']  # example defaults
    )

    if famous_sports:
        fig = helper.gold_age_distribution_by_sport(df, famous_sports)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No Gold medalist age data available for the selected sports.")
    else:
        st.info("Please select at least one sport from the sidebar.")

    sport_list = df['Sport'].dropna().unique().tolist()
    sport_list.sort()
    selected_sport = st.selectbox("Select Sport for Height vs Weight Scatter", sport_list)

    # Get scatter figure from helper
    fig = helper.height_weight_scatter(df, selected_sport)

    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No athlete data available for {selected_sport}.")

    st.markdown(f"### Male vs Female Participation Over the Years in {selected_sport}")
    fig_gender = helper.male_vs_female_participation_sport(df, selected_sport)
    if fig_gender:
        st.plotly_chart(fig_gender, use_container_width=True)
    else:
        st.warning(f"No male/female athlete data available for {selected_sport}.")

    st.markdown("### Male vs Female Participation Over the Years")

    fig = helper.male_vs_female_participation(df)

    st.plotly_chart(fig, use_container_width=True)