import base64
import streamlit as st
import pandas as pd
import altair as alt
import warnings

warnings.filterwarnings('ignore')

def set_bg_image(image_file):
    with open(image_file, "rb") as file:
        btn = base64.b64encode(file.read()).decode()
    st.markdown(f"""<style>.stApp {{background-image: url("data:image/png;base64,{btn}"); background-size: cover;}}</style>""", unsafe_allow_html=True)

set_bg_image("Football_New2.png")

# Function to load the player and team data
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df_player_original = load_data('2017-2023 Football Stats (Cleaned).csv')
df_team_original = load_data('Top5_SquadTotals.csv')
df_filtered_player = df_player_original.copy()
df_filtered_team = df_team_original.copy()

# User's choice: Player Search or Team Search
search_choice = st.radio("Select search type:", ("Player Search", "Team Search"))

if search_choice == "Player Search":
    st.header('Player Search')
    general_search_query = st.text_input("Start typing a player's name for search")
    if general_search_query:
        player_mask = df_player_original['Name'].str.contains(general_search_query, case=False, na=False)
        matching_players = df_player_original.loc[player_mask, 'Name'].unique()
        selected_player = st.selectbox("Player Suggestions", matching_players)
        if selected_player:
            df_filtered_player = df_player_original[df_player_original['Name'] == selected_player]
            if st.checkbox('Show player data'):
                st.write(df_filtered_player)
            if st.checkbox('Visualize Player Data'):
                metrics = [col for col in df_filtered_player.columns if col not in ['Season', 'Name', 'Team', 'Age', 'Nation', 'League', 'Position']]
                selected_metric = st.selectbox("Select player metric to visualize", metrics)
                chart = alt.Chart(df_filtered_player).mark_bar().encode(
                    x='Season',
                    y=selected_metric,
                    color=alt.Color('Season', scale=alt.Scale(scheme='tableau10'))
                )
                st.altair_chart(chart, use_container_width=True)

elif search_choice == "Team Search":
    st.header('Team Search')
    general_search_query = st.text_input("Start typing a team's name for search")
    if general_search_query:
        team_mask = df_team_original['Team'].str.contains(general_search_query, case=False, na=False)
        matching_teams = df_team_original.loc[team_mask, 'Team'].unique()
        selected_team = st.selectbox("Team Suggestions", matching_teams)
        if selected_team:
            df_filtered_team = df_team_original[df_team_original['Team'] == selected_team]
            if st.checkbox('Show team data'):
                st.write(df_filtered_team)
            if st.checkbox('Visualize Team Data'):
                metrics = [col for col in df_filtered_team.columns if col not in ['Season', 'Team', 'League']]
                selected_metric = st.selectbox("Select team metric to visualize", metrics)
                chart = alt.Chart(df_filtered_team).mark_bar().encode(
                    x='Season',
                    y=selected_metric,
                    color=alt.Color('Season', scale=alt.Scale(scheme='tableau10'))
                )
                st.altair_chart(chart, use_container_width=True)
