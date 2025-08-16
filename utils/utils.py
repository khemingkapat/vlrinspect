import re
import pandas as pd
from selectolax.parser import HTMLParser

re_strip = lambda sp, st: sp.join(
    re.findall("\S+", st)
)  # function for normal regex by finding all char


# def get_full_name(abbr: str, full_names: list[str]) -> str:
#     for name in full_names:
#         if abbr.lower() == name.lower() or abbr.lower() in name.lower():
#             return name
#
#         checked_idx = 0
#         for char in name:
#             if char.lower() == abbr[checked_idx].lower():
#                 checked_idx += 1
#
#         if checked_idx == len(abbr):
#             return name
#
#     return ""


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
                    row_data[column_name] = span.text(strip=True)

        data_rows.append(row_data)

    result = pd.DataFrame(data_rows, columns=all_columns)

    result = result.set_index(["Map", "Team", "Name"])

    return result
