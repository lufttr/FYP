import base64
import streamlit as st
import pandas as pd
import joblib
import requests
from io import BytesIO
from joblib import load
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
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

# Initialize session state for selected players if it doesn't exist
if 'selected_players' not in st.session_state:
    st.session_state.selected_players = []

# Function to load the player data
@st.cache_data
def load_player_data():
    try:
        data = pd.read_csv('2017-2023 Football Stats (Cleaned).csv')
        return data
    except Exception as e:
        st.error(f"Error loading player data: {e}")
        return pd.DataFrame()

# Function to load the predicted data
@st.cache_data
def load_predicted_data():
    try:
        data = pd.read_csv('top_scorers.csv')
        return data
    except Exception as e:
        st.error(f"Error loading team data: {e}")
        return pd.DataFrame()

# Load Player Data
df_player_original = load_player_data()

# Load Predicted Data
df_predicted = load_predicted_data()

def dynamic_weighted_average(data, column, recent_seasons=3, recent_season_weight=2):
    """
    Calculate a weighted average where more recent seasons are given higher weights.

    Args:
    data (pd.DataFrame): The DataFrame containing the data.
    column (str): The name of the column to calculate the weighted average for.
    recent_seasons (int): The number of most recent seasons to assign higher weights.
    recent_season_weight (int): The weight multiplier for the most recent seasons.

    Returns:
    float: The weighted average.
    """
    num_records = len(data)
    weights = [1] * num_records  # Start with equal weights

    # Assign higher weights to the most recent seasons
    for i in range(1, recent_seasons + 1):
        if i <= num_records:
            weights[-i] *= recent_season_weight  # Increase weight for recent seasons

    weighted_sum = sum(data[column] * weights)
    total_weights = sum(weights)
    return weighted_sum / total_weights if total_weights > 0 else 0

def add_weighted_goals_feature(df, goal_column='Goals', new_column='Weighted_Goals'):
    # Creating an empty column for weighted goals
    df[new_column] = 0

    for player in df['Name'].unique():
        player_data = df[df['Name'] == player]
        weighted_goals = dynamic_weighted_average(player_data, goal_column)
        df.loc[df['Name'] == player, new_column] = weighted_goals

    return df

# Adding the weighted goals feature
# Create a new DataFrame with the weighted goals feature added
df_with_weighted_goals = add_weighted_goals_feature(df_player_original, goal_column='Goals', new_column='Weighted_Goals')

def predict_future_goals(player_name, dataset, model, preprocessor):
    # Filter the dataset for the player's historical data
    player_data = dataset[dataset['Name'] == player_name]

    # Check if player data is found
    if player_data.empty:
        return f"No data found for player '{player_name}'."

    # Increment age by 1 for prediction of next season
    if 'Age' in player_data.columns:
        player_data['Age'] += 1

    # Make sure 'Weighted_Goals' is updated for prediction
    player_data['Weighted_Goals'] = dynamic_weighted_average(player_data, 'Goals')

    # Exclude target variable and other non-feature columns
    player_data = player_data.drop(['Goals', 'Season', 'Name'], axis=1, errors='ignore')

    # Make the prediction
    processed_player_data = preprocessor.transform(player_data)
    predicted_goals = model.predict(processed_player_data)
    return round(predicted_goals[0])

# Streamlit application layout
st.title("Football Player Future Goals Prediction")

# Load the model, preprocessor, and the new DataFrame with weighted goals
# Cache the function for loading the model
@st.cache(allow_output_mutation=True)
def load_model(url):
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful
    model_file = BytesIO(response.content)
    return joblib.load(model_file)

# Instead of using relative paths, specify the absolute path
model_url = 'https://raw.githubusercontent.com/lufttr/FYP/main/rf_best_model.joblib'
preprocessor_url = 'https://raw.githubusercontent.com/lufttr/FYP/main/preprocessor.joblib'

# Use the cached function to load the model and preprocessor
model = load_model(model_url)
preprocessor = load_model(preprocessor_url)
df_with_weighted_goals = load_player_data()  # Assuming this function now returns the DataFrame with weighted goals

@st.cache_data
def prepare_suggestion_data(df):
    # Process and cache the data for faster access
    # This could involve creating an indexed structure or a simpler list
    unique_names = df['Name'].unique().tolist()
    return unique_names

all_player_names = prepare_suggestion_data(df_player_original)

def get_player_name_suggestions(query, all_names):
    if query and len(query) > 2:
        # Use faster search logic, perhaps with an optimized data structure
        return [name for name in all_names if query.lower() in name.lower()][:10]  # limit to first 10 matches
    return []

# Then use these functions in your Streamlit app
player_search_query = st.text_input("Enter a player's name")
player_name_suggestions = get_player_name_suggestions(player_search_query, all_player_names)

# Display the player selection box with autocomplete-like behavior
selected_player_name = st.selectbox("Player Suggestions", player_name_suggestions)

# Predict button
if st.button("Predict") and selected_player_name:
    predicted_goals = predict_future_goals(selected_player_name, df_with_weighted_goals, model, preprocessor)
    st.write(f"Predicted goals for the next season for {selected_player_name}: {predicted_goals}")

# Streamlit layout
st.title("Top 100 Predicted Goal Scorers")

# Convert goal predictions to whole numbers if they're not already
df_predicted['Predicted_Goals'] = df_predicted['Predicted_Goals'].round().astype(int)

# Checkbox to show/hide the data
if st.checkbox('Show Predicted Goal Scorers'):
    st.subheader("Predicted Top Goal Scorers for Next Season")
    st.dataframe(df_predicted)
