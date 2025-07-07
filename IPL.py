
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

with tabs[0]:
    st.header("Match Results by Team")
    user_input = st.text_input("Enter team name:")
    if user_input:
        team = get_closest_match(user_input, matches['team1'].unique())
        if team:
            csk = (matches['team1'] == team) | (matches['team2'] == team)
            csk_matches = matches[csk]
            csk_won = csk_matches['winner'] == team
            count = csk_won.value_counts()
            result = ['Won', 'Lost']
            total = [count.get(True, 0), count.get(False, 0)]
            fig, ax = plt.subplots()
            bars = ax.bar(result, total, color='yellow')
            for i in range(len(bars)):
                ax.text(i, total[i] + 1, str(total[i]), ha='center')
            ax.set_title(f"Match Results for {team}")
            ax.set_ylabel("Number of Matches")
            st.pyplot(fig)
        else:
            st.error("Team not found.")

with tabs[1]:
    st.header("Player of the Match Awards")
    player_input = st.text_input("Enter player name:")
    if player_input:
        batter = get_closest_match(player_input, deliveries['batter'].unique())
        if batter:
            s = matches[matches['player_of_match'] == batter]
            st.dataframe(s[['season', 'player_of_match']])
            season_counts = s['season'].value_counts().sort_index()
            fig, ax = plt.subplots()
            season_counts.plot(kind='bar', ax=ax)
            for i, v in enumerate(season_counts):
                ax.text(i, v + 0.5, str(v), ha='center')
            ax.set_title(f"Player of the Match Awards by Season: {batter}")
            st.pyplot(fig)
        else:
            st.error("Player not found.")

with tabs[2]:
    st.header("Batting Against Teams")
    player_name = st.text_input("Enter player name:", key="batting")
    if player_name:
        player = get_closest_match(player_name, deliveries['batter'].unique())
        if player:
            dhoni = deliveries[deliveries['batter'] == player]
            d = dhoni.groupby('bowling_team')['batsman_runs'].agg('sum').sort_values(ascending=False)
            st.bar_chart(d)

with tabs[3]:
    st.header("Bowler Analysis for Batsman")
    player_name = st.text_input("Enter player name:", key="bowler")
    if player_name:
        player = get_closest_match(player_name, deliveries['batter'].unique())
        if player:
            dhoni = deliveries[deliveries['batter'] == player]
            c = dhoni.groupby('bowler')['batsman_runs'].agg('sum').sort_values(ascending=False).head(10)
            st.bar_chart(c)

with tabs[4]:
    st.header("Team Result Summary")
    team = st.text_input("Enter team name:", key="team_result")
    if team:
        team = get_closest_match(team, matches['team1'].unique())
        if team:
            winner = matches['winner'].value_counts()
            st.bar_chart(winner)

with tabs[5]:
    st.header("📅 Matches by Season")
    
    # Count matches per season
    season_count = matches['season'].value_counts().sort_index()
    
    # Plot with custom figure
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(season_count.index.astype(str), season_count.values, color='skyblue')

    # Add data labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # Offset label above the bar
                    textcoords="offset points",
                    ha='center', va='bottom')

    ax.set_xlabel("Season")
    ax.set_ylabel("Number of Matches")
    ax.set_title("Matches Played Per IPL Season")
    ax.tick_params(axis='x', rotation=45)

    st.pyplot(fig)

with tabs[6]:
    st.header("Top Batsmen for a Team")
    team = st.text_input("Enter team name:", key="top_batsman")
    if team:
        team = get_closest_match(team, deliveries['batting_team'].unique())
        if team:
            team_data = deliveries[deliveries['batting_team'] == team]
            top_batsmen = team_data.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(10)
            st.bar_chart(top_batsmen)

with tabs[7]:
    st.header("Top 5 Wicket Takers for Team")
    team = st.text_input("Enter team name:", key="top_wickets")
    if team:
        team = get_closest_match(team, deliveries['bowling_team'].unique())
        if team:
            df = deliveries[(deliveries['bowling_team'] == team) & (deliveries['dismissal_kind'].notnull())]
            top_wicket_takers = df['bowler'].value_counts().head(5)
            st.bar_chart(top_wicket_takers)

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
