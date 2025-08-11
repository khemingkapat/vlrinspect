import streamlit as st
import requests
from selectolax.parser import HTMLParser


def get_team_history(
    _session: requests.Session, team_url: str, url: str = "https://www.vlr.gg/"
):
    team_history_response = _session.get(team_url)
    team_history_page = HTMLParser(team_history_response.text)

    past_matches = team_history_page.css("a.wf-card.fc-flex.m-item")
    for match in past_matches:
        print(match.attributes["href"])
    else:
        print("-" * 50)
