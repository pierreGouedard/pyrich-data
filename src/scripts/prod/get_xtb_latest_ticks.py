# Global import
from pathlib import Path
import yaml
import sys
import os

import pandas as pd
from dotenv import load_dotenv

project_path = Path(__file__).parents[3]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xapi_utils import init_api_client, get_latest_ticks
from src.core.xdata_utils import merge_tick_data
from src.core.dev_utils import set_up_logger


if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data"
    log_dir = project_path / 'logs'
    tick_path = data_path / 'xtb' / 'ticks'

    # Parameters
    env_filename = '.env'
    level = 0
    start_datetime = (pd.Timestamp.utcnow() - pd.Timedelta(minutes=2))
    stock_class = 'CFD'

    # Load list of symbols that needs to be tracked
    d_symbols = yaml.safe_load((project_path / 'config' / 'symbol_tracked.yaml').open('r'))
    d_symbols['stock'] = [d for d in d_symbols['stock'] if d['class'] == stock_class]
    l_symbols = [d['symbol'] for cat, l_symbols in d_symbols.items() for d in l_symbols]

    # Load backup config
    backup_period = yaml.safe_load((project_path / 'config' / 'backup.yaml').open('r'))['ticks']

    # Load env
    dotenv_path = project_path / env_filename
    load_dotenv(dotenv_path)

    # Set up logger
    logger = set_up_logger('latest_tick_collection', log_dir)

    # Create & connect to RR socket
    client, ssid = init_api_client(
        {
            'HOST': os.environ['HOST'], 'PORT': os.environ['PORT'],
            'USER_ID': os.environ['USER_ID'], 'PASSWORD': os.environ['PASSWORD']
        },
        logger
    )

    # Get ticks for all symbols
    df_ticks = get_latest_ticks(l_symbols, level, start_datetime, client, logger)

    if df_ticks is None:
        logger.error('df_ticks')
    client.disconnect()

    # Load existing history dataframe, merge new history
    if (tick_path / 'ticks.csv').exists():
        df_prev_ticks = (
            pd.read_csv(tick_path / 'ticks.csv')
            .assign(timestamp=lambda x: pd.to_datetime(x.timestamp, errors='coerce'))
        )
    else:
        df_prev_ticks = None
    df_all_ticks = merge_tick_data(df_ticks, df_prev_ticks)

    # if backup period is met (oldest data older than today - backup period) save a copy of file with prefix
    # 'backup_'
    if not df_all_ticks.empty:
        datetime_backup_limit = pd.Timestamp.utcnow().tz_convert(None) - pd.Timedelta(**backup_period)
        if df_all_ticks.timestamp.min() < datetime_backup_limit:
            df_all_ticks.to_csv(tick_path / 'backup_ticks.csv', index=False)
            os.remove(tick_path / "ticks.csv")
        else:
            df_all_ticks.to_csv(tick_path / 'ticks.csv', index=False)
