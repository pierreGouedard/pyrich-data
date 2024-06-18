from typing import List, Optional

import pandas as pd

CALENDAR_UNIQUE = ('timestamp', 'country', 'title', 'period')
HISTORY_UNIQUE = ('symbol', 'timestamp')
TICK_UNIQUE = ('symbol', 'timestamp')


def merge_calendar_data(
        df_events: pd.DataFrame, df_prev_events: Optional[pd.DataFrame] = None
) -> pd.DataFrame:

    # Get unique events (arbitrary keep first, there exists some better heuristic)
    df_unique_events = df_events.drop_duplicates(subset=CALENDAR_UNIQUE, keep='first')

    # If no prev data return unique events
    if df_prev_events is None:
        return df_unique_events

    # Keep last version of each unique events
    df_all_events = (
        pd.concat([
            df_events.assign(created=pd.Timestamp.utcnow()),
            df_events.assign(created=pd.Timestamp.utcnow() - pd.Timedelta(minutes=10)),
        ])
        .sort_values(by=list(CALENDAR_UNIQUE) + ['created'])
        .drop_duplicates(subset=CALENDAR_UNIQUE, keep='last')
    )

    return df_all_events.drop(columns=['created'])


def merge_historical_data(df_history: pd.DataFrame, df_prev_history: Optional[pd.DataFrame] = None):
    # If no prev data return current
    if df_prev_history is None:
        return df_history

    # Keep most recent version of duplicated history point
    df_all_history = (
        pd.concat([
            df_history.assign(created=pd.Timestamp.utcnow()),
            df_prev_history.assign(created=pd.Timestamp.utcnow() - pd.Timedelta(minutes=10)),
        ])
        .sort_values(by=list(HISTORY_UNIQUE) + ['created'])
        .drop_duplicates(subset=HISTORY_UNIQUE, keep='last')
    )

    return df_all_history.drop(columns=['created'])


def merge_tick_data(df_ticks: pd.DataFrame, df_prev_ticks: Optional[pd.DataFrame] = None):
    # If no prev data return current
    if df_prev_ticks is None:
        return df_ticks

    # Keep most recent version of duplicated ticks
    df_all_ticks = (
        pd.concat([
            df_ticks.assign(created=pd.Timestamp.utcnow()),
            df_prev_ticks.assign(created=pd.Timestamp.utcnow() - pd.Timedelta(minutes=10)),
        ])
        .sort_values(by=list(TICK_UNIQUE) + ['created'])
        .drop_duplicates(subset=TICK_UNIQUE, keep='last')
    )

    return df_all_ticks.drop(columns=['created'])
