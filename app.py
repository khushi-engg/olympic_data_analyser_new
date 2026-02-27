import streamlit as st
import pandas as pd
import preprocessor
import helper
import plotly.express as px
import io
import sys

# ----------------- PAGE CONFIG ----------------- #
st.set_page_config(page_title="Olympics Data Analysis", layout="wide")


# ----------------- LOAD DATA WITH ERROR HANDLING ----------------- #
@st.cache_data
def load_data():
    # Capture print statements
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        df = preprocessor.preprocess()

        # Get all print statements from preprocessor
        preprocessor_logs = captured_output.getvalue()

        if df is None or df.empty:
            st.error("❌ Failed to load Olympics data. Please check if the data files exist.")
            return pd.DataFrame(), preprocessor_logs

        # Verify required columns exist
        required_cols = ['Year', 'region', 'Medal', 'Sport', 'Name', 'City', 'Event', 'NOC']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.warning(f"⚠️ Some columns are missing: {missing_cols}")
            # Add missing columns with default values
            for col in missing_cols:
                df[col] = None

        return df, preprocessor_logs
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return pd.DataFrame(), captured_output.getvalue()
    finally:
        sys.stdout = old_stdout


df, preprocessor_logs = load_data()

# ----------------- DEBUG INFORMATION (NOW WITH PREPROCESSOR LOGS) ----------------- #
with st.expander("🔧 Debug Information - Click to Expand"):
    st.write("### 📋 Preprocessor Logs:")
    st.code(preprocessor_logs)

    st.write("### 📊 DataFrame Info:")
    st.write(f"**Shape:** {df.shape}")
    st.write(f"**Columns:** {df.columns.tolist()}")

    if not df.empty:
        st.write("**First 5 rows:**")
        st.dataframe(df.head())
        st.write("**Year range:**", df['Year'].min(), "to", df['Year'].max())
        st.write("**Unique regions:**", df['region'].nunique() if 'region' in df.columns else "No region column")
        st.write("**Unique sports:**", df['Sport'].nunique() if 'Sport' in df.columns else "No sport column")
        st.success("✅ DataFrame loaded successfully!")
    else:
        st.error("❌ DataFrame is EMPTY!")

# ----------------- CHECK IF DATA IS LOADED ----------------- #
if df.empty:
    st.warning("No data available. Please check the debug information above.")
    st.stop()  # Stop execution if no data

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


# ----------------- HELPER FUNCTION FOR SAFE DATA ACCESS ----------------- #
def safe_dataframe_display(data, use_container_width=True):
    """Safely display dataframe with error handling"""
    try:
        if data is not None and not data.empty:
            st.dataframe(data, use_container_width=use_container_width)
        else:
            st.info("No data available to display")
    except Exception as e:
        st.error(f"Error displaying data: {str(e)}")


# ----------------- MEDAL TALLY ----------------- #
if user_menu == 'Medal Tally':
    st.sidebar.title('Olympics Analysis')
    st.markdown("<h2 style='text-align: center;'>🏅 Medal Tally Analysis</h2>", unsafe_allow_html=True)

    with st.expander("🔎 Show Raw Data"):
        safe_dataframe_display(df)

    st.sidebar.header("Filter Options")

    # Safe year and country list generation
    try:
        years, country = helper.country_year_list(df)
        # Ensure we have at least 'Overall' option
        if not years or len(years) == 0:
            years = ['Overall']
        if not country or len(country) == 0:
            country = ['Overall']
    except Exception as e:
        st.error(f"Error loading filters: {str(e)}")
        years = ['Overall']
        country = ['Overall']

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    # Safe medal tally fetch
    try:
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

        safe_dataframe_display(medal_tally)
    except Exception as e:
        st.error(f"Error displaying medal tally: {str(e)}")

# ----------------- OVERALL ANALYSIS ----------------- #
elif user_menu == 'Overall Analysis':
    st.markdown("<h2 style='text-align: center;'>📊 Overall Analysis</h2>", unsafe_allow_html=True)

    # Safe metrics calculation
    try:
        editions = df['Year'].nunique() - 1 if 'Year' in df.columns else 0
        cities = df['City'].nunique() if 'City' in df.columns else 0
        sports = df['Sport'].nunique() if 'Sport' in df.columns else 0
        events = df['Event'].nunique() if 'Event' in df.columns else 0
        athletes = df['Name'].nunique() if 'Name' in df.columns else 0
        nations = df['region'].nunique() if 'region' in df.columns else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Editions", editions)
        col2.metric("Hosts", cities)
        col3.metric("Sports", sports)

        col1, col2, col3 = st.columns(3)
        col1.metric("Events", events)
        col2.metric("Nations", nations)
        col3.metric("Athletes", athletes)
    except Exception as e:
        st.error(f"Error calculating metrics: {str(e)}")

    # Nations over time
    try:
        nations_over_time = helper.data_over_time(df, "region")
        if not nations_over_time.empty:
            fig = px.line(nations_over_time, x='Edition', y='region', markers=True, line_shape='spline',
                          color_discrete_sequence=['#89CFF0'])
            fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=450)
            fig.update_traces(line=dict(width=3))
            st.title("Participating Nations Over the Years")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for nations over time")
    except Exception as e:
        st.error(f"Error displaying nations over time: {str(e)}")

    # Events over time
    try:
        events_over_time = helper.data_over_time(df, "Event")
        if not events_over_time.empty:
            fig = px.line(events_over_time, x='Edition', y='Event', markers=True, line_shape='spline',
                          color_discrete_sequence=['#A3C1AD'])
            fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=450)
            fig.update_traces(line=dict(width=3))
            st.title("Events Over the Years")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for events over time")
    except Exception as e:
        st.error(f"Error displaying events over time: {str(e)}")

    # Athletes over time
    try:
        athletes_over_time = helper.data_over_time(df, "Name")
        if not athletes_over_time.empty:
            fig = px.line(athletes_over_time, x='Edition', y='Name', markers=True, line_shape='spline',
                          color_discrete_sequence=['#FFD580'])
            fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=450)
            fig.update_traces(line=dict(width=3))
            st.title("Athletes Over the Years")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for athletes over time")
    except Exception as e:
        st.error(f"Error displaying athletes over time: {str(e)}")

    # Heatmap: Events per sport
    try:
        heatmap_data = helper.events_per_sport_over_time(df)
        if not heatmap_data.empty:
            fig = px.imshow(
                heatmap_data,
                labels=dict(x="Year", y="Sport", color="Number of Events"),
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Viridis"
            )
            fig.update_layout(title="Number of Events per Sport Over the Years", xaxis_title="Year",
                              yaxis_title="Sport", height=800)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for events per sport heatmap")
    except Exception as e:
        st.error(f"Error displaying heatmap: {str(e)}")

    # Most successful athletes
    try:
        st.markdown("<h3 style='text-align: center;'>🏅 Most Successful Athletes</h3>", unsafe_allow_html=True)
        sport_list = df['Sport'].dropna().unique().tolist() if 'Sport' in df.columns else []
        sport_list.sort()
        sport_list.insert(0, 'Overall')
        selected_sport = st.selectbox("Select Sport", sport_list, key="overall_athletes")

        top_athletes = helper.most_successful(df, selected_sport)
        if not top_athletes.empty:
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
            fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), height=600,
                              yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No athlete data available")
    except Exception as e:
        st.error(f"Error displaying most successful athletes: {str(e)}")

# ----------------- COUNTRY-WISE ANALYSIS ----------------- #
elif user_menu == 'Country-wise Analysis':
    st.markdown("<h2 style='text-align: center;'>🏅 Country-wise Yearwise Medal Tally</h2>", unsafe_allow_html=True)

    # ----------------- Sidebar country selection ----------------- #
    try:
        country_list = df['region'].dropna().unique().tolist() if 'region' in df.columns else []
        country_list.sort()

        if not country_list:
            st.warning("No country data available")
            st.stop()

        default_index = country_list.index('United States') if 'United States' in country_list else 0
        selected_country = st.sidebar.selectbox(
            "Select a Country",
            country_list,
            index=default_index
        )
    except Exception as e:
        st.error(f"Error loading country list: {str(e)}")
        st.stop()

    # ----------------- Yearwise medal tally table & line ----------------- #
    try:
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
                y='Total Medals',
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
    except Exception as e:
        st.error(f"Error displaying country medal tally: {str(e)}")

    # ----------------- Country-specific sport heatmap ----------------- #
    try:
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
    except Exception as e:
        st.error(f"Error displaying heatmap: {str(e)}")

    # ----------------- Most Successful Athletes ----------------- #
    try:
        st.markdown(f"<h3 style='text-align: center;'>🏅 Most Successful Athletes - {selected_country}</h3>",
                    unsafe_allow_html=True)
        top_athletes = helper.most_successful2(df, selected_country)

        if top_athletes.empty:
            st.warning(f"No athlete data found for {selected_country}.")
        else:
            # Show as table
            st.dataframe(top_athletes[['Name', 'Total Wins', 'Sport']].reset_index(drop=True))

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
    except Exception as e:
        st.error(f"Error displaying most successful athletes: {str(e)}")

# ----------------- ATHLETE-WISE ANALYSIS ----------------- #
elif user_menu == 'Athlete-wise Analysis':
    st.markdown("<h2 style='text-align: center;'>🏃 Athlete Analysis</h2>", unsafe_allow_html=True)

    st.markdown("### Age Distribution of Athletes and Medalists")

    # Get the figure from helper
    try:
        fig = helper.age_distribution(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No age distribution data available")
    except Exception as e:
        st.error(f"Error displaying age distribution: {str(e)}")

    try:
        sport_options = df['Sport'].unique().tolist() if 'Sport' in df.columns else []
        famous_sports = st.sidebar.multiselect(
            "Select Sports for Gold Medalist Age Distribution",
            options=sport_options,
            default=['Athletics', 'Swimming', 'Gymnastics', 'Rowing'] if sport_options else []
        )

        if famous_sports:
            fig = helper.gold_age_distribution_by_sport(df, famous_sports)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No Gold medalist age data available for the selected sports.")
        else:
            st.info("Please select at least one sport from the sidebar.")
    except Exception as e:
        st.error(f"Error displaying gold medalist age distribution: {str(e)}")

    try:
        sport_list = df['Sport'].dropna().unique().tolist() if 'Sport' in df.columns else []
        sport_list.sort()

        if sport_list:
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
    except Exception as e:
        st.error(f"Error displaying sport-specific analysis: {str(e)}")

    try:
        st.markdown("### Male vs Female Participation Over the Years")
        fig = helper.male_vs_female_participation(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No male/female participation data available")
    except Exception as e:
        st.error(f"Error displaying male/female participation: {str(e)}")