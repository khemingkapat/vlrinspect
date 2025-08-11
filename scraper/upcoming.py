import streamlit as st
import requests
from selectolax.parser import HTMLParser


@st.cache_data(ttl=3600)  # Data will be re-scraped after 1 hour (3600 seconds)
def get_upcoming_matches(
    _session: requests.Session, url="https://www.vlr.gg/"
) -> list[dict[str, str]]:

    upcoming_matches_data = []

    response = _session.get(url)
    response.raise_for_status()  # Check for HTTP errors
    tree = HTMLParser(response.text)

    elements = tree.css("a.mod-match")

    for element in elements:
        if not element.css_first("div.h-match-team-score.mod-count.js-spoiler"):
            # Use the new working selector for team names
            team_name_divs = element.css("div.h-match-team-name")
            match_link = str(element.attributes["href"])

            if len(team_name_divs) == 2:

                upcoming_matches_data.append(
                    {
                        "team_a": team_name_divs[0].text(strip=True),
                        "team_b": team_name_divs[1].text(strip=True),
                        "link": url + match_link,
                    }
                )

    return upcoming_matches_data
