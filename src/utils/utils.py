import re
import pandas as pd
from selectolax.parser import HTMLParser
import numpy as np

re_strip = lambda sp, st: sp.join(
    re.findall("\S+", st)
)  # function for normal regex by finding all char


def vectorized_lookup(df: pd.DataFrame, selector_column: str, target_suffix: str):
    target_column_names = df[selector_column] + target_suffix

    target_columns = [col for col in df.columns if col.endswith(target_suffix)]

    column_name_to_index = {col: i for i, col in enumerate(target_columns)}

    column_indices = target_column_names.map(column_name_to_index)

    target_values = df[target_columns].values
    row_indices = np.arange(len(df))

    return target_values[row_indices, column_indices]


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


stat_cols = {
    "r2.0": "Rating 2.0",
    "acs": "ACS",
    "k": "Kill",
    "d": "Death",
    "a": "Assist",
    "+/–": "KD Diff",
    "kast": "KAST",
    "adr": "ADR",
    "hs%": "Headshot %",
    "fk": "First Kill",
    "fd": "First Death",
    "f+/–": "FKD Diff",
}

stat_cols_full = list(stat_cols.values())
stat_cols_short = list(stat_cols.keys())
