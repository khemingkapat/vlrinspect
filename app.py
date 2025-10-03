import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

import streamlit as st
from pages import home_page, overview_page, player_page, map_page

# Configure the page - do this only once at the top level
st.set_page_config(
    page_title="Valorant Team Comparison Dashboard",
    page_icon="🎮",
    layout="wide",  # This makes the app use the full width of the screen
    initial_sidebar_state="expanded",
)


def main():
    # Initialize session state if not exists
    if "team_histories" not in st.session_state:
        st.session_state.team_histories = {}
    if "selected_match_info" not in st.session_state:
        st.session_state.selected_match_info = {}
    if "selected_link" not in st.session_state:
        st.session_state.selected_link = ""

    # Check if we have valid data to show analysis pages
    has_valid_data = (
        bool(st.session_state.get("team_histories", {}))
        and bool(st.session_state.get("selected_match_info", {}))
        and bool(st.session_state.get("selected_link", ""))
    )

    if not has_valid_data:
        # Show only the home page
        home_page()
    else:
        # Define pages for navigation (excluding home since we handle it separately)
        pages = {
            "Analysis": [
                st.Page(overview_page, title="Overview", icon="📊"),
                st.Page(player_page, title="Player", icon="🚹"),
                st.Page(map_page, title="Map", icon="🗺️"),
            ]
        }

        # Create navigation
        page = st.navigation(pages)

        # Add sidebar info and controls
        st.sidebar.markdown("---")
        st.sidebar.info("Valorant Team Comparison Tool")

        # Show current match info in sidebar
        if st.session_state.get("selected_match_info"):
            match_name = st.session_state.selected_match_info.get("match_name", "")
            st.sidebar.success(f"Current Match: {match_name}")

        # Add button to return to home page
        if st.sidebar.button("Select New Match", type="secondary"):
            # Clear session state and return to home
            for key in ["team_histories", "selected_match_info", "selected_link"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        # Run the selected page
        page.run()


if __name__ == "__main__":
    main()
