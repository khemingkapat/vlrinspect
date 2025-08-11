import requests
from selectolax.parser import HTMLParser
import re

re_strip = lambda sp, st: sp.join(
    re.findall("\S+", st)
)  # function for normal regex by finding all char


def get_team_history(
    _session: requests.Session,
    team_url: str,
    head: int = -1,
    url: str = "https://www.vlr.gg/",
) -> list[str]:
    team_history_response = _session.get(team_url)
    team_history_page = HTMLParser(team_history_response.text)

    past_matches = team_history_page.css("a.wf-card.fc-flex.m-item")

    if head == -1:
        head = len(past_matches)

    result = []
    for match in past_matches[:head]:
        result.append(url + str(match.attributes["href"]))

    return result


def scrape_match_info(
    _session: requests.Session, match_url: str, url: str = "https://www.vlr.gg/"
):
    match_response = _session.get(match_url)
    match_html = HTMLParser(match_response.text)

    match_name = match_html.css_first("title").text().strip().split(" | ")[0].strip()
    print(match_name)

    match_result = re_strip("", match_html.css_first("div.js-spoiler").text())
    print(match_result)

    ban_pick = re_strip(
        " ", match_html.css_first("div.match-header-note").text()
    ).split(";")
    print(ban_pick)
