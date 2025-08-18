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


def detect_type(value: str):
    if value.lower() in {"none", "null", "nil"}:
        return None

    if value.lower() in {"true", "false"}:
        return value.lower() == "true"

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    if "%" in value:
        return int(value.replace("%", "")) / 100

    return value
