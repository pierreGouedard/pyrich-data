# Global import
from pathlib import Path
import logging
import sys
import os
from dotenv import load_dotenv

import pandas as pd

project_path = Path(__file__).parents[3]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xApi_utils import init_api_client, d_period_mapping, get_historical_data


if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data"
    output_path = data_path / 'xtb' / 'examples' / 'history'

    # Parameters
    env_filename = '.env'
    symbol = 'AI.FR_9'
    period = 1
    start_date: pd.Timestamp = (pd.Timestamp.utcnow() - pd.Timedelta(days=20)).floor('D')

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
    df_data = get_historical_data(symbol, period, start_date, client, logger)
    client.disconnect()

    if df_data is not None:
        end_date = df_data.timestamp.dt.date.max()
        df_data.to_csv(
            output_path / f'{symbol}_{d_period_mapping[period]}_{start_date}_{end_date}.csv', index=False
        )

