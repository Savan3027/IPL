import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from difflib import get_close_matches

st.set_page_config(page_title="IPL Smart Dashboard", layout="wide")
st.title("🏏 IPL Analysis Dashboard with Typo Tolerance")

@st.cache_data
def load_data():
    matches = pd.read_csv("https://drive.google.com/uc?id=1PAgRqv7J76lR6Ogew7xqsKm3YP0dR5o_")
    deliveries = pd.read_csv("https://drive.google.com/uc?id=1KD5HPSS9Bk5sd2Q-JHByAKkbuB8yOGJK")
    return matches, deliveries

matches, deliveries = load_data()

def get_closest_match(name, options):
    match = get_close_matches(name, options, n=1, cutoff=0.5)
    return match[0] if match else None

tabs = st.tabs([
    "Match Results",
    "Player of Match",
    "Bowling by Team",
    "Bowler Summary",
    "Team Result",
    "Season Summary",
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
            bars = ax.bar(['Won', 'Lost'], [wins, losses], color='orange')
            for i in range(len(bars)):
                ax.text(i, bars[i].get_height() + 1, str(int(bars[i].get_height())), ha='center')
            ax.set_title(f"Match Results for {team}")
            st.pyplot(fig)
        else:
            st.error("Team not found.")

# 2. Player of the Match
with tabs[1]:
    st.header("Player of the Match Awards")
    player_input = st.text_input("Enter player name:")

    if player_input:
        # Drop NaNs and convert to strings for safe fuzzy matching
        player_list = matches['player_of_match'].dropna().astype(str).unique()
        player_name = get_closest_match(player_input, player_list)

        if player_name:
            player_df = matches[matches['player_of_match'] == player_name]

            # Group by season and count (like your notebook output)
            season_awards = player_df['season'].value_counts().sort_index()
            st.write("### Awards by Season")
            st.dataframe(season_awards.rename("count"))

            # Plot the bar chart
            fig, ax = plt.subplots()
            bars = ax.bar(season_awards.index.astype(str), season_awards.values, color='lightgreen')
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height}", xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points", ha='center')
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
            d = df.groupby('bowling_team')['batsman_runs'].agg('sum').sort_values(ascending=False)
            st.bar_chart(d)

# 4. Bowler Summary
with tabs[3]:
    st.header("Bowler Analysis for Batsman")
    player_name = st.text_input("Enter player name:", key="bowler")
    if player_name:
        player = get_closest_match(player_name, deliveries['batter'].unique())
        if player:
            df = deliveries[deliveries['batter'] == player]
            c = df.groupby('bowler')['batsman_runs'].agg('sum').sort_values(ascending=False).head(10)
            st.bar_chart(c)

# 5. Team Result
with tabs[4]:
    st.header("Team Result Summary")
    team = st.text_input("Enter team name:", key="team_result")
    if team:
        team = get_closest_match(team, matches['team1'].unique())
        if team:
            winner = matches['winner'].value_counts()
            st.bar_chart(winner)

# 6. Season Summary
with tabs[5]:
    st.header("📅 Matches by Season")
    season_count = matches['season'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(season_count.index.astype(str), season_count.values, color='skyblue')
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    ax.set_xlabel("Season")
    ax.set_ylabel("Number of Matches")
    ax.set_title("Matches Played Per IPL Season")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

# 7. Top Batsman
with tabs[6]:
    st.header("Top Batsmen for a Team")
    team = st.text_input("Enter team name:", key="top_batsman")
    if team:
        team = get_closest_match(team, deliveries['batting_team'].unique())
        if team:
            team_data = deliveries[deliveries['batting_team'] == team]
            top_batsmen = team_data.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(10)
            st.bar_chart(top_batsmen)

# 8. Top Wicket Takers
with tabs[7]:
    st.header("Top 5 Wicket Takers for Team")
    team = st.text_input("Enter team name:", key="top_wickets")
    if team:
        team = get_closest_match(team, deliveries['bowling_team'].unique())
        if team:
            df = deliveries[(deliveries['bowling_team'] == team) & (deliveries['dismissal_kind'].notnull())]
            top_wicket_takers = df['bowler'].value_counts().head(5)
            st.bar_chart(top_wicket_takers)

# 9. Powerplay Runs
with tabs[8]:
    st.header("Powerplay Runs (Overs 1–6)")
    team = st.text_input("Enter team name:", key="powerplay")
    if team:
        team = get_closest_match(team, deliveries['batting_team'].unique())
        if team:
            deliveries['over'] = deliveries['over'].astype(int)
            pp = deliveries[(deliveries['over'] <= 6) & (deliveries['batting_team'] == team)]
            runs_by_batsman = pp.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10)
            st.bar_chart(runs_by_batsman)

# 10. Toss Win Match Win
with tabs[9]:
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
