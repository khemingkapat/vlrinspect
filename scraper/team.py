import requests
from selectolax.parser import HTMLParser


def get_teams_from_match(
    _session: requests.Session, match_url: str, url: str = "https://www.vlr.gg/"
) -> list[str]:
    match_response = _session.get(match_url)
    match_page = HTMLParser(match_response.text)

    teams = [
        str(team.attributes["href"]) for team in match_page.css("a.match-header-link")
    ]

    if len(teams) != 2:
        raise ValueError

    result = []
    for team in teams:
        team_response = _session.get(url + team.replace("/team/", "/team/matches/"))
        team_page = HTMLParser(team_response.text)
        core_id_element = team_page.css("span.wf-dropdown a[href*='?core_id=']")

        latest_core_id = str(core_id_element[1].attributes["href"])
        result.append(url + latest_core_id)
    return result
