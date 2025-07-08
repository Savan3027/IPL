import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from difflib import get_close_matches
import matplotlib.cm as cm

st.set_page_config(page_title="IPL Analysis Dashboard", layout="wide")
st.title("🏏 IPL Analysis Dashboard")

# Load data from Google Drive
@st.cache_data
def load_data():
    matches = pd.read_csv("https://drive.google.com/uc?id=1PAgRqv7J76lR6Ogew7xqsKm3YP0dR5o_")
    deliveries = pd.read_csv("https://drive.google.com/uc?id=1KD5HPSS9Bk5sd2Q-JHByAKkbuB8yOGJK")
    return matches, deliveries

matches, deliveries = load_data()

def get_closest_match(name, options):
    name = str(name)
    options = [str(opt) for opt in options]
    match = get_close_matches(name, options, n=1, cutoff=0.5)
    return match[0] if match else None

tabs = st.tabs([
    "Match Results",
    "Player of Match",
    "Bowling by Team",
    "Bowler Summary",
    "Top Batsman",
    "Top Wicket Takers",
    "Powerplay Runs",
    "Toss Win Match Win"
])

# 1. Match Results
with tabs[0]:
    st.header("Match Results by Team")
    user_input = st.text_input("Enter team name:")
    if user_input:
        team = get_closest_match(user_input, matches['team1'].unique())
        if team:
            mask = (matches['team1'] == team) | (matches['team2'] == team)
            team_matches = matches[mask]
            wins = (team_matches['winner'] == team).sum()
            total = len(team_matches)
            losses = total - wins
            fig, ax = plt.subplots()
            bars = ax.bar(['Won', 'Lost'], [wins, losses], color=['limegreen', 'crimson'])
            for bar in bars:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, str(int(bar.get_height())), ha='center')
            ax.set_title(f"Match Results for {team}")
            st.pyplot(fig)
        else:
            st.error("Team not found.")

# 2. Player of the Match
with tabs[1]:
    st.header("Player of the Match Awards")
    player_input = st.text_input("Enter player name:")
    if player_input:
        player_list = matches['player_of_match'].dropna().astype(str).unique()
        player_name = get_closest_match(player_input, player_list)
        if player_name:
            player_df = matches[matches['player_of_match'] == player_name]
            season_awards = player_df['season'].value_counts().sort_index()
            st.write("### Awards by Season")
            st.dataframe(season_awards.rename("Count"))

            fig, ax = plt.subplots()
            bars = ax.bar(season_awards.index.astype(str), season_awards.values, color=cm.Set2.colors)
            ax.bar_label(bars)
            ax.set_ylabel("Awards")
            ax.set_xlabel("Season")
            ax.set_title(f"{player_name} - Player of the Match Awards by Season")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)
        else:
            st.warning("Player not found.")

# 3. Bowling by Team
with tabs[2]:
    st.header("Batting Against Teams")
    player_name = st.text_input("Enter player name:", key="batting")
    if player_name:
        player = get_closest_match(player_name, deliveries['batter'].unique())
        if player:
            df = deliveries[deliveries['batter'] == player]
            grouped = df.groupby('bowling_team')['batsman_runs'].sum().sort_values(ascending=False)
            fig, ax = plt.subplots()
            bars = ax.bar(grouped.index, grouped.values, color=cm.tab10.colors)
            ax.bar_label(bars)
            ax.set_title(f"{player} vs Bowling Teams")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)

# 4. Bowler Summary
with tabs[3]:
    st.header("Bowler Analysis for Batsman")
    player_name = st.text_input("Enter player name:", key="bowler")
    if player_name:
        player = get_closest_match(player_name, deliveries['batter'].unique())
        if player:
            df = deliveries[deliveries['batter'] == player]
            grouped = df.groupby('bowler')['batsman_runs'].sum().sort_values(ascending=False).head(10)
            fig, ax = plt.subplots()
            bars = ax.bar(grouped.index, grouped.values, color=cm.Dark2.colors)
            ax.bar_label(bars)
            ax.set_title(f"{player} vs Bowlers (Top 10)")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)

# 5. Top Batsman
with tabs[4]:
    st.header("Top Batsmen for a Team")
    team = st.text_input("Enter team name:", key="top_batsman")
    if team:
        team = get_closest_match(team, deliveries['batting_team'].unique())
        if team:
            team_data = deliveries[deliveries['batting_team'] == team]
            top_batsmen = team_data.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(10)
            fig, ax = plt.subplots()
            bars = ax.bar(top_batsmen.index, top_batsmen.values, color=cm.Set1.colors)
            ax.bar_label(bars)
            ax.set_title(f"Top 10 Batsmen for {team}")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)

# 6. Top Wicket Takers
with tabs[5]:
    st.header("Top 5 Wicket Takers for Team")
    team = st.text_input("Enter team name:", key="top_wickets")
    if team:
        team = get_closest_match(team, deliveries['bowling_team'].unique())
        if team:
            df = deliveries[(deliveries['bowling_team'] == team) & (deliveries['dismissal_kind'].notnull())]
            top_wicket_takers = df['bowler'].value_counts().head(5)
            fig, ax = plt.subplots()
            bars = ax.bar(top_wicket_takers.index, top_wicket_takers.values, color=cm.Accent.colors)
            ax.bar_label(bars)
            ax.set_title(f"Top 5 Wicket Takers for {team}")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)

# 7. Powerplay Runs
with tabs[6]:
    st.header("Powerplay Runs (Overs 1–6)")
    team = st.text_input("Enter team name:", key="powerplay")
    if team:
        team = get_closest_match(team, deliveries['batting_team'].unique())
        if team:
            deliveries['over'] = deliveries['over'].astype(int)
            pp = deliveries[(deliveries['over'] <= 6) & (deliveries['batting_team'] == team)]
            runs_by_batsman = pp.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10)
            fig, ax = plt.subplots()
            bars = ax.bar(runs_by_batsman.index, runs_by_batsman.values, color=cm.Paired.colors)
            ax.bar_label(bars)
            ax.set_title(f"Top Powerplay Run Scorers - {team}")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)

# 8. Toss Win Match Win
with tabs[7]:
    st.header("Toss Win Match Win Percentage")
    team = st.text_input("Enter team name:", key="toss_win")
    if team:
        team = get_closest_match(team, matches['toss_winner'].unique())
        if team:
            toss_winning_team = matches[matches['toss_winner'] == team]
            t = toss_winning_team['winner'] == toss_winning_team['toss_winner']
            total_toss_win = t.count()
            total_match_win = t.sum()
            win_percentage = round((total_match_win * 100) / total_toss_win, 2) if total_toss_win > 0 else 0
            st.write("Total Toss Win:", total_toss_win)
            st.write("Total Match Win:", total_match_win)
            st.write("Winning Percentage:", win_percentage, "%")
