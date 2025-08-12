import requests
from selectolax.parser import HTMLParser
from utils import re_strip


def get_team_history_list(
    _session: requests.Session,
    team_url: str,
    head: int = -1,
    url: str = "https://www.vlr.gg/",
) -> tuple[list[str], dict[str, str]]:
    team_history_response = _session.get(team_url)
    team_history_page = HTMLParser(team_history_response.text)

    first_abbr = {
        team_history_page.css_first("h1.wf-title")
        .text(): team_history_page.css_first("h2.wf-title.team-header-tag")
        .text()
    }

    all_abbr = first_abbr.copy()

    for key, val in first_abbr.items():
        all_abbr[val] = key
    past_matches = team_history_page.css("a.wf-card.fc-flex.m-item")

    if head == -1:
        head = len(past_matches)

    result = []
    for match in past_matches[:head]:
        result.append(url + str(match.attributes["href"]))

    return result, all_abbr


def scrape_matches(
    _session: requests.Session,
    matches_url: list[str],
    team_abbreviate: dict[str, str],
    url: str = "https://www.vlr.gg/",
):
    for match in matches_url:
        scrape_match_info(
            _session=_session, match_url=match, team_abbreviate=team_abbreviate
        )


def scrape_match_info(
    _session: requests.Session,
    match_url: str,
    team_abbreviate: dict[str, str],
    url: str = "https://www.vlr.gg/",
):
    print(team_abbreviate)
    match_response = _session.get(match_url)
    match_html = HTMLParser(match_response.text)

    match_name = (
        match_html.css_first("title").text().strip().split(" | ")[0].split(" vs. ")
    )
    print(match_name)

    # match_result = re_strip("", match_html.css_first("div.js-spoiler").text())
    # print(match_result)

    ban_pick = re_strip(
        " ", match_html.css_first("div.match-header-note").text()
    ).split(";")

    for ban_str in ban_pick:
        ban_list = ban_str.strip().split(" ")
        if ban_list[-1].lower() == "remains":
            continue
        name, act, mapp = ban_list
        print(f"{team_abbreviate.get(name)} {act} {mapp}")
