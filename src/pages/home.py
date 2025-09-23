import streamlit as st
from scraper import Scraper
import requests
import time


def home_page():
    url = "https://www.vlr.gg/"
    st.title("Upcoming VLR Matches")

    # Initialize session
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )

    # Initialize session state variables if they don't exist
    if "team_histories" not in st.session_state:
        st.session_state.team_histories = {}
    if "selected_match_info" not in st.session_state:
        st.session_state.selected_match_info = {}
    if "selected_link" not in st.session_state:
        st.session_state.selected_link = ""

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
            st.session_state.selected_link = selected_link
            st.info(f"Selected match link: {selected_link}")

            # Get team names from selected match
            teams = selected_match_name.split(" vs. ")
            team1_name = teams[0]
            team2_name = teams[1]

            # Store team histories in session state as organized dictionary
            team1_history, team2_history = Scraper.get_team_history(
                session, selected_link, head=20
            )

            st.session_state.team_histories = {
                "team1": {"name": team1_name, "history": team1_history},
                "team2": {"name": team2_name, "history": team2_history},
            }

            # Store additional match info
            st.session_state.selected_match_info = {
                "match_name": selected_match_name,
                "link": selected_link,
                "team1_name": team1_name,
                "team2_name": team2_name,
            }

            print(f"Team 1 ({team1_name}):", team1_history)
            print(f"Team 2 ({team2_name}):", team2_history)
