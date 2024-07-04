# Global import
from pathlib import Path
import sys
import os
import pandas as pd

project_path = Path(__file__).parents[3]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xdata_utils import merge_tick_data, merge_historical_data, merge_calendar_data


def clean_tmp_dir(pth: Path, key: str):
    for filename in os.listdir(pth):
        if key in filename:
            os.remove(pth / filename)


if __name__ == '__main__':
    # Get paths
    consolidated_data_path = project_path / "data" / "xtb" / "consolidated_data"

    # Compute consolidated ticks
    pth_tmp_ticks = consolidated_data_path / 'tmp_ticks'
    pth_ticks = consolidated_data_path / 'ticks.csv'

    # Load all freshly downloaded ticks data
    l_dfs = []
    for filename in os.listdir(pth_tmp_ticks):
        if 'ticks' not in filename:
            continue

        # Append df
        l_dfs.append(pd.read_csv(pth_tmp_ticks / filename))

    if l_dfs:
        df_consolidated_ticks, df_tmp_ticks = None, pd.concat(l_dfs)
        if pth_ticks.exists():
            # Merge
            df_consolidated_ticks = merge_tick_data(df_tmp_ticks, pd.read_csv(pth_ticks))
        else:
            df_consolidated_ticks = merge_tick_data(df_tmp_ticks, None)

        if df_consolidated_ticks is not None:
            df_consolidated_ticks.to_csv(pth_ticks, index=False)

    # Clean tick tmp dir
    clean_tmp_dir(pth_tmp_ticks, 'ticks')
    print('************ ticks data consolidated *****************')

    # Compute consolidated history
    pth_tmp_history = consolidated_data_path / 'tmp_history'
    pth_history = consolidated_data_path / 'history.csv'

    # Load all freshly downloaded history data
    l_dfs = []
    for filename in os.listdir(pth_tmp_history):
        if 'history' not in filename:
            continue

        # Append df
        l_dfs.append(pd.read_csv(pth_tmp_history / filename))

    if l_dfs:
        df_consolidated_history, df_tmp_history = None, pd.concat(l_dfs)
        if pth_history.exists():
            # Merge
            df_consolidated_history = merge_historical_data(df_tmp_history, pd.read_csv(pth_history))
        else:
            df_consolidated_history = merge_historical_data(df_tmp_history, None)

        if df_consolidated_history is not None:
            df_consolidated_history.to_csv(pth_history, index=False)

    # Clean tick tmp dir
    clean_tmp_dir(pth_tmp_history, 'history')
    print('************ history data consolidated *****************')

    # Compute consolidated events
    pth_tmp_events = consolidated_data_path / 'tmp_events.csv'
    pth_events = consolidated_data_path / 'events.csv'

    # Load all freshly downloaded event data
    l_dfs = []
    for filename in os.listdir(pth_tmp_events):
        if 'events' not in filename:
            continue

        # Append df
        l_dfs.append(pd.read_csv(pth_tmp_events / filename))

    if l_dfs:
        df_consolidated_events, df_tmp_events = None, pd.concat(l_dfs)
        if pth_events.exists():
            # Merge
            df_consolidated_events = merge_calendar_data(df_tmp_events, pd.read_csv(pth_events))
        else:
            df_consolidated_events = merge_calendar_data(df_tmp_events, None)

        if df_consolidated_events is not None:
            df_consolidated_events.to_csv(pth_events, index=False)

    # Clean tick tmp dir
    clean_tmp_dir(pth_tmp_events, 'events')
    print('************ event data consolidated *****************')
