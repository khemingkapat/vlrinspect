import streamlit as st
from scraper import Scraper
import requests
import time
from selectolax.parser import HTMLParser

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
    # Prepare the options list for the selectbox
    options = [f"{match['team_a']} vs. {match['team_b']}" for match in match_data]

    # Create a mapping from display name to link
    link_map = {
        f"{match['team_a']} vs. {match['team_b']}": match["link"]
        for match in match_data
    }

    # Use st.selectbox for a dropdown selector
    selected_match_name = st.selectbox(
        "Select an upcoming match:",
        options=options,
        index=0,  # Set a default selection
    )

    # Use the selected name to get the link from the map
    selected_link = link_map.get(selected_match_name, None)

    # Display the selected link
    if selected_link:
        st.info(f"Selected match link: {selected_link}")
else:
    st.info("No upcoming matches found or an error occurred. Please try again later.")


match_response = session.get(selected_link)
match_page = HTMLParser(match_response.text)

teams = [team.attributes["href"] for team in match_page.css("a.match-header-link")]
example_team = teams[0]

team_response = session.get(url + example_team.replace("/team/", "/team/matches/"))
team_page = HTMLParser(team_response.text)
core_id_element = team_page.css("span.wf-dropdown a[href*='?core_id=']")

latest_core_id = str(core_id_element[1].attributes["href"])

team_history_response = session.get(url + latest_core_id)
team_history_page = HTMLParser(team_history_response.text)

past_matches = team_history_page.css("a.wf-card.fc-flex.m-item")
for match in past_matches:
    print(match.attributes["href"])
else:
    print("-" * 50)
