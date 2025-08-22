import streamlit as st
from scraper import Scraper
import requests
import time

url = "https://www.vlr.gg/"

st.set_page_config(layout="wide")
st.title("Upcoming VLR Matches")


session = requests.Session()
session.headers.update(
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
)

selected_link = ""
with st.spinner("Fetching upcoming match data..."):
    # Pass the session to the function
    match_data = Scraper.get_upcoming_matches(session, url=url)
    time.sleep(2)  # Add a small delay for better user experience


if match_data:
    options = [f"{match['team_a']} vs. {match['team_b']}" for match in match_data]
    link_map = {
        f"{match['team_a']} vs. {match['team_b']}": match["link"]
        for match in match_data
    }

    options.insert(0, "Select Your Match")  # Add a placeholder at the beginning

    selected_match_name = st.selectbox(
        "Select an upcoming match:",
        options=options,
        index=0,
    )

if selected_match_name != "Select Your Match":
    selected_link = link_map.get(selected_match_name, "")
    st.info(f"Selected match link: {selected_link}")

    Scraper.get_team_history(session, selected_link)

    # team1, team2 = Scraper.get_teams_from_match(session, selected_link)
    # print(team1, team2)
    # team1_history = Scraper.get_team_history(session, team1, head=5)
    # Scraper.scrape_match_info(session, team1_history[0])
