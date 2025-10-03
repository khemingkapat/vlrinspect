import streamlit as st
from src.scraper import Scraper
import requests
import time
import re


def validate_vlr_link(link):
    """
    Validate if the provided link is a valid VLR.gg match link.
    Returns tuple: (is_valid, error_message)
    """
    if not link:
        return False, "Please enter a link"

    # Pattern for VLR match links: https://www.vlr.gg/{number}/{team1}-vs-{team2}-{tournament}-{stage}
    pattern = r"^https?://(?:www\.)?vlr\.gg/\d+/[\w-]+-vs-[\w-]+.*$"

    if not re.match(pattern, link):
        return (
            False,
            "Invalid VLR.gg match link format. Expected format: https://www.vlr.gg/[match-id]/[team1]-vs-[team2]-[tournament]-[stage]",
        )

    return True, ""


def extract_teams_from_link(link):
    """
    Extract team names from VLR match link.
    Returns tuple: (team1_name, team2_name) or (None, None) if extraction fails
    """
    try:
        # Extract the match slug part (between match ID and tournament)
        match = re.search(r"/\d+/([\w-]+-vs-[\w-]+)", link)
        if match:
            match_slug = match.group(1)
            # Split by '-vs-' to get team names
            teams = match_slug.split("-vs-")
            if len(teams) >= 2:
                # Convert kebab-case to Title Case
                team1 = " ".join(word.capitalize() for word in teams[0].split("-"))
                team2 = " ".join(word.capitalize() for word in teams[1].split("-"))
                return team1, team2
    except Exception as e:
        st.error(f"Error extracting team names: {str(e)}")

    return None, None


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

    # Add match history limit selector (global for both tabs)
    st.sidebar.header("⚙️ Settings")
    match_limit = st.sidebar.slider(
        "Number of matches to scrape per team:",
        min_value=1,
        max_value=30,
        value=10,
        help="Select how many historical matches to analyze for each team",
    )
    st.sidebar.info(f"Will scrape **{match_limit}** matches for each team")

    # Add tabs for different input methods
    tab1, tab2 = st.tabs(["📋 Select from Upcoming Matches", "🔗 Enter Custom Link"])

    with tab1:
        with st.spinner("Fetching upcoming match data..."):
            match_data = Scraper.get_upcoming_matches(session, url=url)
            time.sleep(2)

        if match_data:
            options = [
                f"{match['team_a']} vs. {match['team_b']}" for match in match_data
            ]
            link_map = {
                f"{match['team_a']} vs. {match['team_b']}": match["link"]
                for match in match_data
            }
            options.insert(0, "Select Your Match")

            selected_match_name = st.selectbox(
                "Select an upcoming match:",
                options=options,
                index=0,
            )

            if selected_match_name != "Select Your Match":
                selected_link = link_map.get(selected_match_name, "")

                # Check if this is a new selection
                if st.session_state.selected_link != selected_link:
                    st.session_state.selected_link = selected_link
                    st.info(f"Selected match link: {selected_link}")

                    teams = selected_match_name.split(" vs. ")
                    team1_name = teams[0]
                    team2_name = teams[1]

                    with st.spinner("Loading match data..."):
                        process_match_data(
                            session,
                            selected_link,
                            team1_name,
                            team2_name,
                            selected_match_name,
                            match_limit,
                        )

                    # Trigger rerun to redirect
                    st.rerun()
                else:
                    st.info(f"Selected match link: {selected_link}")

    with tab2:
        st.write("Enter a VLR.gg match link to analyze:")
        st.caption(
            "Example: https://www.vlr.gg/542270/fnatic-vs-nrg-valorant-champions-2025-ubf"
        )

        custom_link = st.text_input(
            "Match Link:", placeholder="https://www.vlr.gg/...", key="custom_link_input"
        )

        if st.button("Load Match Data", type="primary"):
            is_valid, error_msg = validate_vlr_link(custom_link)

            if not is_valid:
                st.error(error_msg)
            else:
                # Try to extract team names from link
                team1_name, team2_name = extract_teams_from_link(custom_link)

                if team1_name and team2_name:
                    st.success(f"✅ Valid link detected: {team1_name} vs. {team2_name}")

                    with st.spinner("Loading match data..."):
                        try:
                            st.session_state.selected_link = custom_link
                            match_name = f"{team1_name} vs. {team2_name}"
                            process_match_data(
                                session,
                                custom_link,
                                team1_name,
                                team2_name,
                                match_name,
                                match_limit,
                            )
                            st.success("Match data loaded successfully!")

                            # Trigger rerun to redirect
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error loading match data: {str(e)}")
                            st.info(
                                "Please verify the link is correct and the match exists on VLR.gg"
                            )
                else:
                    st.error(
                        "Could not extract team names from the link. Please check the format."
                    )


def process_match_data(
    session, selected_link, team1_name, team2_name, match_name, match_limit=10
):
    """
    Process and store match data in session state

    Args:
        session: requests Session object
        selected_link: VLR match URL
        team1_name: Name of first team
        team2_name: Name of second team
        match_name: Display name of the match
        match_limit: Number of historical matches to scrape (default: 10)
    """
    team1_history, team2_history = Scraper.get_team_history(
        session, selected_link, head=match_limit
    )

    st.session_state.team_histories = {
        "team1": {"name": team1_name, "history": team1_history},
        "team2": {"name": team2_name, "history": team2_history},
    }

    st.session_state.selected_match_info = {
        "match_name": match_name,
        "link": selected_link,
        "team1_name": team1_name,
        "team2_name": team2_name,
        "match_limit": match_limit,
    }
