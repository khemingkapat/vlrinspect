import requests
from selectolax.parser import HTMLParser
import pandas as pd
from datetime import datetime
from src.utils import detect_type, vectorized_lookup
from models import Match, Matches, MatchHistory, Game, Games
from typing import Optional


def get_team_history_list(
    _session: requests.Session,
    team_url: str,
    url: str = "https://www.vlr.gg/",
) -> tuple[list[str], dict[str, str]]:
    team_history_response = _session.get(team_url)
    team_history_page = HTMLParser(team_history_response.text)

    full_name_node = team_history_page.css_first("h1.wf-title")
    abbr_name_node = team_history_page.css_first("h2.wf-title.team-header-tag")

    if abbr_name_node is None:
        abbr_name_node = full_name_node

    first_abbr = {full_name_node.text(strip=True): abbr_name_node.text(strip=True)}

    all_abbr = first_abbr.copy()

    for key, val in first_abbr.items():
        all_abbr[val] = key
    past_matches = team_history_page.css("a.wf-card.fc-flex.m-item")

    result = []
    for match in past_matches:
        result.append(url + str(match.attributes["href"])[1:])

    return result, all_abbr


def scrape_matches(
    _session: requests.Session,
    matches_url: list[str],
    head: int,
    team_abbreviate: dict[str, str],
    full_name: str,
    url: str = "https://www.vlr.gg/",
) -> MatchHistory:

    result = []

    if head == -1:
        head = len(matches_url)

    idx = 0
    while len(result) < head or idx == len(matches_url):
        # print(f"working on {matches_url[idx]}")
        result.append(
            scrape_match_info(
                _session=_session,
                match_url=matches_url[idx],
                team_abbreviate=team_abbreviate,
            )
        )
        idx += 1

    matches = Matches(result)
    match_history = MatchHistory(full_name, team_abbreviate[full_name], matches)
    return match_history


def extract_round_result_from_html(
    html: str, map_name: str, game_id: int
) -> pd.DataFrame:
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
            winning_side = ["atk", "def"]["mod-ct" in winner.attributes.get("class")]

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
        data, columns=["phase", "round_num", "winning_side", "reason", "current_score"]
    )

    round_result.loc[:, "game_id"] = [game_id] * len(round_result)
    round_result.loc[:, "map"] = [map_name] * len(round_result)

    round_result.loc[:11, "phase"] = "first_half"
    round_result.loc[12 : min(round_result["round_num"].max(), 23), "phase"] = (
        "second_half"
    )

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
    round_result.loc[:, "winning_team"] = vectorized_lookup(
        round_result, "winning_side", "_team"
    )

    index_cols = ["game_id", "map", "phase", "round_num"]
    if len(round_result) < 13:
        return pd.DataFrame(columns=round_result.columns).set_index(index_cols)

    return round_result.set_index(index_cols)


def extract_overview_from_html(html: str, map_name: str, game_id: int) -> pd.DataFrame:
    tree = HTMLParser(html)
    side_list = ["all", "atk", "def"]
    headers = [th.text(strip=True) for th in tree.css("table thead tr th")][2:]
    headers[-1] = "F" + headers[-1]

    side_stat_cols = []
    for side in side_list:
        for header in headers:
            side_stat_cols.append(f"{header}_{side}")

    all_columns = ["game_id", "map", "team", "name", "agent"] + side_stat_cols

    data_rows = []

    for tr in tree.css("table tbody tr"):
        name = tr.css_first("div.text-of").text(strip=True)
        team = tr.css_first("div.ge-text-light").text(strip=True)
        agent_elem = tr.css_first("img")
        agent = agent_elem.attributes.get("alt", None) if agent_elem else None

        row_data = {
            "game_id": game_id,
            "map": map_name,
            "team": team,
            "name": name,
            "agent": agent,
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
                    side = "all"
                elif "mod-t" in classes:
                    side = "atk"
                elif "mod-ct" in classes:
                    side = "def"

                if side:
                    column_name = f"{col}_{side}"
                    row_data[column_name] = detect_type(span.text(strip=True))

        data_rows.append(row_data)

    result = pd.DataFrame(data_rows, columns=all_columns)

    index_cols = ["game_id", "map", "team", "name"]
    result.rename(columns={col: col.lower() for col in result.columns}, inplace=True)
    if len(result) != 5:
        return pd.DataFrame(columns=result.columns).set_index(index_cols)

    return result.set_index(index_cols)


def extract_economy_from_html(html: str, map_name: str, game_id: int) -> pd.DataFrame:
    tree = HTMLParser(html)
    divs = tree.css('div[style*="overflow-x: auto"]')

    get_buy_type = lambda sign: (
        "full-eco"
        if not sign
        else sign.replace("$$$", "full-buy")
        .replace("$$", "semi-buy")
        .replace("$", "semi-eco")
    )

    if len(divs) < 2:
        return pd.DataFrame()
    div = divs[1]

    if div is None:
        return pd.DataFrame()

    econ_table = div.css_first("table.wf-table-inset.mod-econ")
    rows = econ_table.css("tr")
    data_rows = []

    round_adder = 0
    phase = ["first_half", "second_half", "overtime"]
    for phase, row in zip(phase, rows):
        teams, *wins = row.css("td")
        teams_order = [team.text(strip=True) for team in teams.css("div.team")]

        first_win = wins[0].css_first("div.rnd-sq.mod-win")
        attacker_on = 0
        if "mod-t" in first_win.attributes.get("class"):
            attacker_on = 0
        else:
            attacker_on = 1

        defender_on = int(not bool(attacker_on))
        overtime_counter = 1
        for round_num, win in enumerate(wins, start=1):
            if phase == "overtime":
                phase_str = f"overtime_{overtime_counter}"
            else:
                phase_str = phase
            boxes = win.css("div.rnd-sq")
            data_rows.append(
                {
                    "game_id": game_id,
                    "map": map_name,
                    "phase": phase_str,
                    "round_num": round_num + round_adder,
                    "atk_buytype": get_buy_type(boxes[attacker_on].text(strip=True)),
                    "def_buytype": get_buy_type(boxes[defender_on].text(strip=True)),
                }
            )
            overtime_counter += 1
        round_adder += 12

    index_cols = ["game_id", "map", "phase", "round_num"]
    econ_df = pd.DataFrame(data_rows)

    if len(econ_df) < 13:
        return pd.DataFrame(columns=econ_df.columns).set_index(index_cols)

    econ_df.loc[0, ["atk_buytype", "def_buytype"]] = ["pistol"] * 2
    econ_df.loc[12, ["atk_buytype", "def_buytype"]] = ["pistol"] * 2

    return econ_df.set_index(index_cols)


def scrape_match_info(
    _session: requests.Session,
    match_url: str,
    team_abbreviate: dict[str, str],
    url: str = "https://www.vlr.gg/",
) -> Optional[Match]:
    try:
        match_response = _session.get(match_url)
        econ_response = _session.get(f"{match_url}?game=all&tab=economy")
        match_response.raise_for_status()
        econ_response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

    match_id = int(match_url.removeprefix(url).split("/")[0])

    match_html = HTMLParser(match_response.text)
    econ_html = HTMLParser(econ_response.text)

    # --- 2. Crucial Data Scraping and Validation ---
    teams_node = match_html.css_first("title")
    event_name_node = match_html.css_first("a.match-header-event div > div")
    stage_name_node = match_html.css_first("div.match-header-event-series")
    match_date_data = match_html.css_first("div.moment-tz-convert")
    match_score_node = match_html.css_first("div.js-spoiler")

    if not all(
        [
            teams_node,
            event_name_node,
            stage_name_node,
            match_date_data,
            match_score_node,
        ]
    ):
        print("Missing crucial top-level data.")
        return None

    try:
        teams = teams_node.text().strip().split(" | ")[0].split(" vs. ")
        event_name = event_name_node.text(strip=True)
        stage_name = (
            stage_name_node.text(strip=True).replace("\t", "").replace("\n", "")
        )
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
            map_name = m.text(strip=True).split("\n")[0][1:]
            map_ids.append((map_name, data_game_id))

    if not maps:
        map_div_node = match_html.css_first("div.vm-stats-game.mod-active")
        if map_div_node is None:
            return None

        map_id = map_div_node.attributes.get("data-game-id", "")
        map_name = map_div_node.css_first("div.map").css_first("span").text(strip=True)
        map_ids.append((map_name, map_id))

    games_data = []
    for map_name, map_id in map_ids:

        div_map = match_html.css_first(f'div.vm-stats-game[data-game-id="{map_id}"]')
        if not div_map:
            print(f"Skipping map {map_id} due to missing data.")
            continue

        map_teams = div_map.css("div.vm-stats-game-header div.team")
        map_winner = ""
        map_win_score = 0
        for team in map_teams:
            team_name = team.css_first("div.team-name").text(strip=True)
            team_score = int(team.css_first("div.score").text(strip=True))
            if team_score > map_win_score:
                map_win_score = team_score
                map_winner = team_name

        div_econ = econ_html.css_first(f'div.vm-stats-game[data-game-id="{map_id}"]')

        econ_df = extract_economy_from_html(div_econ.html, map_name, int(map_id))

        # Assume extract_round_result_from_html and extract_df_from_html are robust
        round_result_df = extract_round_result_from_html(
            div_map.html, map_name, int(map_id)
        )

        stat_tables = div_map.css("table.wf-table-inset.mod-overview")
        overview_df = pd.DataFrame()
        for table in stat_tables:
            overview_df = pd.concat(
                [
                    overview_df,
                    extract_overview_from_html(table.html, map_name, int(map_id)),
                ]
            )

        if len(round_result_df) != len(econ_df):
            continue
        combined_round_result_df = pd.concat([round_result_df, econ_df], axis=1)

        combined_round_result_df = combined_round_result_df.assign(
            losing_side = combined_round_result_df.winning_side.map({"atk":"def","def":"atk"})
        )

        combined_round_result_df = combined_round_result_df.assign(
            winner_buytype=vectorized_lookup(
                combined_round_result_df, "winning_side", "_buytype"
            ),
            loser_buytype=vectorized_lookup(
                combined_round_result_df, "losing_side", "_buytype"
            )
        )
        games_data.append(
            Game(
                map_name=map_name,
                game_id=int(map_id),
                winner=map_winner,
                round_result=combined_round_result_df,
                overview=overview_df,
            )
        )
    games = Games(games_data)

    # --- 6. Return Pydantic Object ---
    return Match(
        match_id=match_id,
        patch=patch,
        teams=teams,
        event_name=event_name,
        stage_name=stage_name,
        match_date=match_date,
        match_result=match_result,
        team_abbreviation=team_abbreviate,
        winner=max(match_result, key=match_result.get),
        match_url=match_url,
        pick_ban=pick_ban_df,
        games=games,
    )
