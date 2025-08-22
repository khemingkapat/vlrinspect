import requests
from selectolax.parser import HTMLParser
from utils import re_strip
import pandas as pd
from datetime import datetime
from utils import detect_type
from models import Match
from typing import Optional


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
        result.append(url + str(match.attributes["href"])[1:])

    return result, all_abbr


def scrape_matches(
    _session: requests.Session,
    matches_url: list[str],
    team_abbreviate: dict[str, str],
    url: str = "https://www.vlr.gg/",
) -> list[Match]:

    result = []
    for match in matches_url:
        print(f"working on {match}")
        result.append(
            scrape_match_info(
                _session=_session, match_url=match, team_abbreviate=team_abbreviate
            )
        )
    return result


def extract_round_result_from_html(html: str, map_name: str) -> pd.DataFrame:
    tree = HTMLParser(html)
    game_phase = tree.css("div.vlr-rounds-row")
    opp_side = {
        "Attack": "Defense",
        "Defense": "Attack",
    }

    phase_side = dict()
    data = []

    if len(game_phase) <= 0:
        return pd.DataFrame()

    for phase, row in zip(["Normal", "Overtime"], game_phase):
        for round in (
            rounds := row.css("div.vlr-rounds-row-col[title]:not(.mod-spacing)")
        ):
            winner = round.css_first("div.rnd-sq.mod-win")
            if winner is None:
                continue
            winning_side = ["Attack", "Defense"][
                "mod-ct" in winner.attributes.get("class")
            ]

            current_score = round.attributes["title"]

            win_reason = (
                winner.css_first("img")
                .attributes.get("src")
                .split("/")[-1]
                .removesuffix(".webp")
            )

            round_num = int(round.css_first("div.rnd-num").text(strip=True))

            data.append(
                [phase, int(round_num), winning_side, win_reason, current_score]
            )

        team_order = row.css("div.team")
        first_win = rounds[0].css("div.rnd-sq")

        win_order = 0
        if "mod-win" in first_win[0].attributes.get("class"):
            win_order = 0
        else:
            win_order = 1

        start_side = "Attack"
        if "mod-t" in first_win[win_order].attributes.get("class"):
            start_side = "Attack"
        else:
            start_side = "Defense"

        phase_side[phase] = {
            team_order[win_order].text(strip=True): start_side,
            team_order[0 if win_order else 1].text(strip=True): opp_side[start_side],
        }

    round_result = pd.DataFrame(
        data, columns=["phase", "round", "winning_side", "reason", "current_score"]
    )

    round_result.loc[:, "map"] = [map_name] * len(round_result)

    round_result.loc[:11, "phase"] = "first_half"
    round_result.loc[12 : min(round_result["round"].max(), 23), "phase"] = "second_half"

    if len(round_result) > 24:
        round_result.loc[24:, "phase"] = [
            f"overtime_{i}" for i in range(1, len(round_result) - 24 + 1)
        ]

    game_phase_side = dict()
    game_phase_side["second_half"] = {
        k: opp_side[v] for k, v in phase_side["Normal"].items()
    } | {opp_side[v]: k for k, v in phase_side["Normal"].items()}

    game_phase_side["first_half"] = phase_side["Normal"] | {
        v: k for k, v in phase_side["Normal"].items()
    }
    if "Overtime" in phase_side:
        game_phase_side["overtime_1"] = phase_side["Overtime"] | {
            v: k for k, v in phase_side["Overtime"].items()
        }

        for ot in range(2, len(round_result) - 24 + 1):
            if ot % 2 == 0:
                game_phase_side[f"overtime_{ot}"] = {
                    k: opp_side[v] for k, v in phase_side["Overtime"].items()
                } | {opp_side[v]: k for k, v in phase_side["Overtime"].items()}
            else:
                game_phase_side[f"overtime_{ot}"] = phase_side["Overtime"] | {
                    v: k for k, v in phase_side["Overtime"].items()
                }

    round_result.loc[:, "atk_team"] = round_result["phase"].map(
        lambda p: game_phase_side[p]["Attack"]
    )
    round_result.loc[:, "def_team"] = round_result["phase"].map(
        lambda p: game_phase_side[p]["Defense"]
    )

    index_cols = ["map", "phase", "round"]
    if len(round_result) < 13:
        return pd.DataFrame(columns=round_result.columns).set_index(index_cols)

    return round_result.set_index(index_cols)


def extract_df_from_html(html: str, map_name: str) -> pd.DataFrame:
    tree = HTMLParser(html)
    side_list = ["All", "Attack", "Defense"]
    headers = [th.text(strip=True) for th in tree.css("table thead tr th")][2:]

    side_stat_cols = []
    for side in side_list:
        for header in headers:
            side_stat_cols.append(f"{header}_{side}")

    all_columns = ["Map", "Team", "Name", "Agent"] + side_stat_cols

    data_rows = []

    for tr in tree.css("table tbody tr"):
        name = tr.css_first("div.text-of").text(strip=True)
        team = tr.css_first("div.ge-text-light").text(strip=True)
        agent_elem = tr.css_first("img")
        agent = agent_elem.attributes.get("alt", None) if agent_elem else None

        row_data = {
            "Map": map_name,
            "Team": team,
            "Name": name,
            "Agent": agent,
        }

        for idx, td in enumerate(tr.css("td:not(.mod-player):not(.mod-agents)")):
            if idx >= len(headers):
                break

            spans = td.css("span")
            col = headers[idx]

            for span in spans:
                classes = span.attributes.get("class", "")
                if not classes:
                    continue

                side = None
                if "mod-both" in classes:
                    side = "All"
                elif "mod-t" in classes:
                    side = "Attack"
                elif "mod-ct" in classes:
                    side = "Defense"

                if side:
                    column_name = f"{col}_{side}"
                    row_data[column_name] = detect_type(span.text(strip=True))

        data_rows.append(row_data)

    result = pd.DataFrame(data_rows, columns=all_columns)

    index_cols = ["Map", "Team", "Name"]
    if len(result) != 5:
        return pd.DataFrame(columns=result.columns).set_index(index_cols)

    return result.set_index(index_cols)


def scrape_match_info(
    _session: requests.Session,
    match_url: str,
    team_abbreviate: dict[str, str],
    url: str = "https://www.vlr.gg/",
) -> Optional[Match]:
    # --- 1. Basic Request Error Handling ---
    try:
        match_response = _session.get(match_url)
        match_response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

    match_html = HTMLParser(match_response.text)

    # --- 2. Crucial Data Scraping and Validation ---
    teams_node = match_html.css_first("title")
    event_name_node = match_html.css_first("a.match-header-event div > div")
    match_date_data = match_html.css_first("div.moment-tz-convert")
    match_score_node = match_html.css_first("div.js-spoiler")

    if not all([teams_node, event_name_node, match_date_data, match_score_node]):
        print("Missing crucial top-level data.")
        return None

    try:
        teams = teams_node.text().strip().split(" | ")[0].split(" vs. ")
        event_name = event_name_node.text(strip=True)
        match_date = datetime.strptime(
            match_date_data.attributes.get("data-utc-ts"), "%Y-%m-%d %H:%M:%S"
        )
        match_score_text = match_score_node.text(strip=True)
        scores = [int(s) for s in match_score_text.split(":")]

        match_result = {teams[0]: scores[0], teams[1]: scores[1]}

    except (IndexError, ValueError) as e:
        print(f"Error parsing crucial data: {e}")
        return None

    # --- 3. Optional Data Scraping ---
    patch = float(-1)
    try:
        patch = float(
            match_html.css_first("div.match-header-super")
            .css_first("""div[style="margin-top: 4px;"]""")
            .css_first("""div[style="font-style: italic;"]""")
            .text(strip=True)
            .removeprefix("Patch ")
        )
    except (AttributeError, ValueError):
        print("No Patch Found, letting patch as -1")

    pick_ban_df = pd.DataFrame()
    pick_ban_node = match_html.css_first("div.match-header-note")
    if pick_ban_node is not None:
        try:
            pick_ban = pick_ban_node.text(strip=True).split(";")
            pick_ban_data = []
            for ban_str in pick_ban:
                ban_list = ban_str.strip().split(" ")
                if len(ban_list) < 3:
                    continue
                if ban_list[-1].lower() == "remains":
                    continue
                name, act, mapp = ban_list
                pick_ban_data.append([team_abbreviate.get(name), act, mapp])
            pick_ban_df = pd.DataFrame(pick_ban_data, columns=["team", "action", "map"])
            pick_ban_df.set_index("team", inplace=True)
        except Exception as e:
            print(f"Error scraping pick/ban data: {e}")
            pick_ban_df = pd.DataFrame()

    # --- 4. Iterating through Maps and Sub-Tables ---
    maps = match_html.css("div.vm-stats-gamesnav-item.js-map-switch")
    map_ids = []
    for m in maps:
        data_game_id = m.attributes.get("data-game-id")
        if (
            data_game_id
            and m.attributes.get("data-disabled") != "1"
            and "All Maps" not in m.text()
        ):
            map_name = m.text(strip=True).split("\n")[0]
            map_ids.append((map_name, data_game_id))

    if not maps:
        map_div_node = match_html.css_first("div.vm-stats-game.mod-active")
        if map_div_node is None:
            return None

        map_id = map_div_node.attributes.get("data-game-id", "")
        map_name = map_div_node.css_first("div.map").css_first("span").text(strip=True)
        map_ids.append((map_name, map_id))

    overview_df = pd.DataFrame()
    round_result_df = pd.DataFrame()

    for map_name, map_id in map_ids:
        div_map = match_html.css_first(f'div.vm-stats-game[data-game-id="{map_id}"]')
        if not div_map:
            print(f"Skipping map {map_id} due to missing data.")
            continue

        # Assume extract_round_result_from_html and extract_df_from_html are robust
        round_result_df = pd.concat(
            [round_result_df, extract_round_result_from_html(div_map.html, map_name)]
        )

        stat_tables = div_map.css("table.wf-table-inset.mod-overview")
        for table in stat_tables:
            overview_df = pd.concat(
                [overview_df, extract_df_from_html(table.html, map_name)]
            )

    # --- 5. Final Consistency Checks ---
    if len(overview_df) == 0 or len(overview_df) != len(map_ids) * 10:
        print(overview_df.shape)
        print("Final consistency check failed for 'overview_df'")
        return None

    if len(round_result_df) < 13 * len(map_ids):
        print("Final consistency check failed for 'round_result_df'")
        return None

    # --- 6. Return Pydantic Object ---
    return Match(
        patch=patch,
        teams=teams,
        event_name=event_name,
        match_date=match_date,
        match_result=match_result,
        team_abbreviation=team_abbreviate,
        pick_ban=pick_ban_df,
        round_result=round_result_df,
        overview=overview_df,
    )
