# Global import
from pathlib import Path
import sys
import os
import pandas as pd

project_path = Path(__file__).parents[3]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xdata_utils import merge_tick_data, merge_historical_data, merge_calendar_data


if __name__ == '__main__':
    # Get paths
    consolidated_data_path = project_path / "data" / "xtb" / "consolidated_data"

    # Get ticks freqhly download if exists

    # Compute consolidated ticks
    pth_tmp_ticks = consolidated_data_path / 'tmp_ticks.csv'
    pth_ticks = consolidated_data_path / 'ticks.csv'

    df_consolidated_ticks = None
    if pth_ticks.exists():
        if pth_tmp_ticks.exists():
            df_consolidated_ticks = merge_tick_data(pd.read_csv(pth_tmp_ticks), pd.read_csv(pth_ticks))
            os.remove(pth_tmp_ticks)
    elif pth_tmp_ticks.exists():
        df_consolidated_ticks = pd.read_csv(pth_tmp_ticks)
        os.remove(pth_tmp_ticks)

    if df_consolidated_ticks is not None:
        df_consolidated_ticks.to_csv(pth_ticks, index=False)

    # Compute consolidated history
    pth_tmp_history = consolidated_data_path / 'tmp_history.csv'
    pth_history = consolidated_data_path / 'history.csv'

    df_consolidated_history = None
    if pth_history.exists():
        if pth_tmp_history.exists():
            df_consolidated_history = merge_historical_data(pd.read_csv(pth_tmp_history), pd.read_csv(pth_history))
            os.remove(pth_tmp_history)

    elif pth_tmp_history.exists():
        df_consolidated_history = pd.read_csv(pth_tmp_history)
        os.remove(pth_tmp_history)

    if df_consolidated_history is not None:
        df_consolidated_history.to_csv(pth_history, index=False)

    # Compute consolidated events
    pth_tmp_event = consolidated_data_path / 'tmp_events.csv'
    pth_event = consolidated_data_path / 'events.csv'

    df_consolidated_event = None
    if pth_event.exists():
        if pth_tmp_event.exists():
            df_consolidated_event = merge_calendar_data(pd.read_csv(pth_tmp_event), pd.read_csv(pth_event))
            os.remove(pth_tmp_event)

    elif pth_tmp_event.exists():
        df_consolidated_event = pd.read_csv(pth_tmp_event)
        os.remove(pth_tmp_event)

    if df_consolidated_event is not None:
        df_consolidated_event.to_csv(pth_event, index=False)
