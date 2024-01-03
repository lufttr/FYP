import base64
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import warnings

warnings.filterwarnings('ignore')

def set_bg_image(image_file):
    with open(image_file, "rb") as file:
        btn = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{btn}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg_image("Football_New2.png")

if 'selected_players' not in st.session_state:
    st.session_state.selected_players = []
if 'selected_team' not in st.session_state:
    st.session_state.selected_team = []

def load_player_data():
    try:
        return pd.read_csv('2017-2023 Football Stats (Cleaned).csv')
    except Exception as e:
        st.error(f"Error loading player data: {e}")
        return pd.DataFrame()
    
def load_team_data():
    try:
        return pd.read_csv('Top5_SquadTotals.csv')
    except Exception as e:
        st.error(f"Error loading team data: {e}")
        return pd.DataFrame()

df_player_original = load_player_data()
df_team_original = load_team_data()

st.header('Comparison')
comparison_type = st.radio("Select comparison type", ["Player", "Team"])

def create_plotly_comparison_chart(data, metric_column, title, group_column):
    fig = go.Figure()

    unique_groups = data[group_column].unique()
    colors = ['indianred', 'royalblue', 'mediumseagreen', 'peachpuff', 'orchid', 'turquoise', 'lightcoral', 'salmon', 'darkkhaki'] 

    for idx, group in enumerate(unique_groups):
        filtered_data = data[data[group_column] == group]
        fig.add_trace(go.Bar(
            x=filtered_data['Season'],
            y=filtered_data[metric_column],
            name=group,
            marker_color=colors[idx % len(colors)]
        ))

    # Updating layout
    fig.update_layout(
        title=title,
        xaxis_title='Season',
        yaxis_title=metric_column,
        barmode='group'
    )

    st.plotly_chart(fig, use_container_width=True)

if comparison_type == "Player":
    comparison_search_query = st.text_input("Start typing a player's name for comparison suggestions")
    comparison_filtered_player_names = df_player_original['Name'].unique()
    if comparison_search_query:
        comparison_filtered_player_names = [name for name in comparison_filtered_player_names if comparison_search_query.lower() in name.lower()]
    options = list(set(comparison_filtered_player_names) | set(st.session_state.get('selected_players', [])))
    player_selection = st.multiselect('Select players to compare', options=options, default=st.session_state.get('selected_players', []))
    
    if player_selection != st.session_state.get('selected_players', []):
        st.session_state['selected_players'] = player_selection
    
    # Exclude certain columns from the multiselect options
    columns_to_exclude = ['Season', 'League', 'Team', 'Name', 'Nation', 'Position']
    columns_to_compare_player = st.multiselect(
        'Select columns to compare (Player dataset)', 
        [col for col in df_player_original.columns if col not in columns_to_exclude]
    )
    
    if st.checkbox("Visualize Player Comparison"):
        combined_df = pd.DataFrame()
        for player in st.session_state['selected_players']:
            player_df = df_player_original[df_player_original['Name'] == player].reset_index(drop=True)
            player_df['Player'] = player
            combined_df = pd.concat([combined_df, player_df])  # Concatenate player data

        for column in columns_to_compare_player:
            if 'Season' in combined_df.columns and column in combined_df.columns:
                filtered_data = combined_df[['Season', 'Player', column]].rename(columns={column: 'Value'})
                create_plotly_comparison_chart(filtered_data, 'Value', f"Comparison of {column} over Seasons", "Player")


if comparison_type == "Team":
    comparison_search_query = st.text_input("Start typing a team's name for comparison suggestions")
    comparison_filtered_team_names = df_team_original['Team'].unique()
    if comparison_search_query:
        comparison_filtered_team_names = [name for name in comparison_filtered_team_names if comparison_search_query.lower() in name.lower()]
    options = list(set(comparison_filtered_team_names) | set(st.session_state.get('selected_teams', [])))
    team_selection = st.multiselect('Select teams to compare', options=options, default=st.session_state.get('selected_teams', []))
    
    if team_selection != st.session_state.get('selected_teams', []):
        st.session_state['selected_teams'] = team_selection

    # Exclude certain columns from the multiselect options
    columns_to_exclude = ['Season', 'League', 'Team']
    columns_to_compare_team = st.multiselect(
        'Select columns to compare (Team dataset)', 
        [col for col in df_team_original.columns if col not in columns_to_exclude]
    )
    
    if st.checkbox("Visualize Team Comparison"):
        combined_df = pd.DataFrame()
        for team in st.session_state['selected_teams']:
            team_df = df_team_original[df_team_original['Team'] == team].reset_index(drop=True)
            team_df['Team'] = team
            combined_df = pd.concat([combined_df, team_df])

        for column in columns_to_compare_team:
            if 'Season' in combined_df.columns and column in combined_df.columns and column != 'Season':
                filtered_data = combined_df[['Season', 'Team', column]].rename(columns={column: 'Value'})
                create_plotly_comparison_chart(filtered_data, 'Value', f"Comparison of {column} over Seasons", "Team")
