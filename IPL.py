import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="IPL Data Explorer", layout="wide")
st.title("🏏 IPL Comprehensive Analysis Dashboard")

# Load data
@st.cache_data
def load_data():
    matches_url = "https://drive.google.com/uc?id=1PAgRqv7J76lR6Ogew7xqsKm3YP0dR5o_"
    deliveries_url = "https://drive.google.com/uc?id=1KD5HPSS9Bk5sd2Q-JHByAKkbuB8yOGJK"
    matches = pd.read_csv(matches_url)
    deliveries = pd.read_csv(deliveries_url)
    return matches, deliveries

matches, deliveries = load_data()

# Sidebar options
st.sidebar.header("Select Analysis")
options = st.sidebar.radio("Choose an analysis:", (
    "Overview",
    "Toss Decision",
    "Toss Win vs Match Win",
    "Match Results by Team",
    "Player of the Match",
    "Batsman vs Teams",
    "Batsman vs Bowlers",
    "Team Statistics",
    "Top Batsmen",
    "Top Wicket Takers",
    "Powerplay Runs"
))

# Overview
if options == "Overview":
    st.header("Dataset Overview")
    st.subheader("Matches Data")
    st.dataframe(matches.head())
    st.subheader("Deliveries Data")
    st.dataframe(deliveries.head())

# Toss Decision
elif options == "Toss Decision":
    st.header("Toss Decision Distribution")
    toss_decision = matches['toss_decision'].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(toss_decision, labels=toss_decision.index, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

# Toss Win vs Match Win
elif options == "Toss Win vs Match Win":
    st.header("Toss Win vs Match Win Analysis")
    team_name = st.text_input("Enter the name of the team:")
    if team_name:
        toss_winning_team = matches[matches['toss_winner'] == team_name]
        t = toss_winning_team['winner'] == toss_winning_team['toss_winner']
        total_toss_win = t.count()
        total_match_win = t.sum()
        win_percentage = round((total_match_win * 100) / total_toss_win, 2) if total_toss_win > 0 else 0

        st.write("Total Toss Win:", total_toss_win)
        st.write("Total Match Win:", total_match_win)
        st.write("Winning Percentage:", win_percentage, "%")

# Match Results by Team
elif options == "Match Results by Team":
    team = st.text_input("Enter the team name:")
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

# Player of the Match
elif options == "Player of the Match":
    player = st.text_input("Enter player name:")
    if player:
        player_clean = player.strip().lower()
        df = matches[matches['player_of_match'].str.lower() == player_clean]
        if not df.empty:
            st.subheader(f"Player of the Match Awards: {player.strip()}")
            if 'season' in df.columns and 'player_of_match' in df.columns:
                st.dataframe(df[['season', 'player_of_match']])
            else:
                st.dataframe(df)

            season_counts = df['season'].value_counts().sort_index()
            fig, ax = plt.subplots()
            season_counts.plot(kind='bar', ax=ax)
            for i, v in enumerate(season_counts):
                ax.text(i, v + 0.5, str(v), ha='center')
            ax.set_title(f"Player of the Match by Season: {player.strip()}")
            st.pyplot(fig)
        else:
            st.warning("Player not found or has no awards.")

# Batsman vs Teams
elif options == "Batsman vs Teams":
    player = st.text_input("Enter batsman name:")
    if player:
        df = deliveries[deliveries['batter'].str.lower() == player.strip().lower()]
        grouped = df.groupby('bowling_team')['batsman_runs'].sum().sort_values(ascending=False)
        st.bar_chart(grouped)

# Batsman vs Bowlers
elif options == "Batsman vs Bowlers":
    player = st.text_input("Enter batsman name:")
    if player:
        df = deliveries[deliveries['batter'].str.lower() == player.strip().lower()]
        grouped = df.groupby('bowler')['batsman_runs'].sum().sort_values(ascending=False).head(10)
        st.bar_chart(grouped)

# Team Statistics
elif options == "Team Statistics":
    team_col = st.selectbox("Select team-related column:", ["winner", "toss_winner", "team1", "team2"])
    team_counts = matches[team_col].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=team_counts.index, y=team_counts.values, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_title(f"Distribution by {team_col}")
    st.pyplot(fig)

# Top Batsmen (based on selected team)
elif options == "Top Batsmen":
    team = st.text_input("Enter the team name (e.g., Mumbai Indians):")
    if team:
        team_data = deliveries[deliveries['batting_team'].str.lower() == team.strip().lower()]
        if not team_data.empty:
            top_batsmen = team_data.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(10)
            st.subheader(f"Top 10 Batsmen for {team.strip()}")
            st.bar_chart(top_batsmen)
        else:
            st.warning("Team not found or no batting data available.")

# Top Wicket Takers (based on selected team)
elif options == "Top Wicket Takers":
    team = st.text_input("Enter the team name (for bowling analysis):")
    if team:
        df = deliveries[(deliveries['bowling_team'].str.lower() == team.strip().lower()) & (deliveries['dismissal_kind'].notnull())]
        if not df.empty:
            top_bowlers = df['bowler'].value_counts().head(10)
            st.subheader(f"Top 10 Wicket Takers for {team.strip()}")
            st.bar_chart(top_bowlers)
        else:
            st.warning("Team not found or no bowling data available.")

# Powerplay Runs (based on selected team)
elif options == "Powerplay Runs":
    st.header("Powerplay Run Analysis (Overs 1–6)")
    team = st.text_input("Enter the team name:")
    if team:
        deliveries['over'] = deliveries['over'].astype(int)
        pp = deliveries[(deliveries['over'] <= 6) & (deliveries['batting_team'].str.lower() == team.strip().lower())]
        if not pp.empty:
            runs_by_batsman = pp.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10)
            st.subheader(f"Top Powerplay Scorers for {team.strip()}")
            st.bar_chart(runs_by_batsman)
        else:
            st.warning("No powerplay data found for this team.")

st.success("✅ All modules are now updated to follow your logic exactly.")
