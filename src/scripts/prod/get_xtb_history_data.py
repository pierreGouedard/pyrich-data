# Global import
from pathlib import Path
import yaml
import logging
import sys
import os
from dotenv import load_dotenv

import pandas as pd

project_path = Path(__file__).parents[3]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xapi_utils import init_api_client, get_historical_data
from src.core.xdata_utils import merge_historical_data

if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data"
    history_path = data_path / 'xtb' / 'history'

    # Parameters
    env_filename = '.env'
    period = 1
    start_date: pd.Timestamp = (pd.Timestamp.utcnow() - pd.Timedelta(days=20)).floor('D')
    stock_class = 'CFD'

    # Load list of symbols that needs to be tracked
    d_symbols = yaml.safe_load((project_path / 'config' / 'symbol_tracked.yaml').open('r'))
    d_symbols['stock'] = [d for d in d_symbols['stock'] if d['class'] == stock_class]
    l_symbols = [d['symbol'] for cat, l_symbols in d_symbols.items() for d in l_symbols]

    # Load backup config
    backup_period = yaml.safe_load((project_path / 'config' / 'backup.yaml').open('r'))['history']

    # Load env
    dotenv_path = project_path / env_filename
    load_dotenv(dotenv_path)

    # logger properties
    logger = logging.getLogger("jsonSocket")
    FORMAT = '[%(asctime)-15s][%(funcName)s:%(lineno)d] %(message)s'
    logging.basicConfig(format=FORMAT)
    logger.setLevel(logging.INFO)

    # Create & connect to RR socket
    client, ssid = init_api_client(
        {
            'HOST': os.environ['HOST'], 'PORT': os.environ['PORT'],
            'USER_ID': os.environ['USER_ID'], 'PASSWORD': os.environ['PASSWORD']
        },
        logger
    )

    # Get minute graph data for a particular symbol
    l_data = []
    for symbol in l_symbols:
        df_history = get_historical_data(symbol, period, start_date, client, logger)

        # Store result if any
        if df_history is None:
            continue
        elif df_history.empty:
            continue
        else:
            l_data.append(df_history.assign(symbol=symbol))

    # Disconnect client
    client.disconnect()

    # Merge symbol's history
    df_history = pd.concat([d for d in l_data])

    # Load existing history dataframe, merge new history
    if (history_path / 'history.csv').exists():
        df_prev_history = (
            pd.read_csv(history_path / 'history.csv')
            .assign(timestamp=lambda x: pd.to_datetime(x.timestamp))
        )
    else:
        df_prev_history = None
    df_all_history = merge_historical_data(df_history, df_prev_history)

    # if backup period is met (oldest data older than today - backup period) save a copy of file with prefix
    # 'backup_'
    datetime_backup_limit = pd.Timestamp.utcnow().tz_convert(None) - pd.Timedelta(**backup_period)
    if df_all_history.timestamp.min() < datetime_backup_limit:
        df_all_history.to_csv(history_path / 'backup_history.csv', index=False)
        os.remove(history_path / "history.csv")
    else:

        df_all_history.to_csv(history_path / 'history.csv', index=False)
