# Global import
from pathlib import Path
import logging
import sys
import os

import pandas as pd
from dotenv import load_dotenv

project_path = Path(__file__).parents[3]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xapi_utils import init_api_client, get_latest_ticks


if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data"
    output_path = data_path / 'xtb' / 'examples' / 'ticks'

    # Parameters
    env_filename = '.env'
    symbols = ['AI.FR_9', 'BAYN.DE_9']
    level = 0
    start_datetime: pd.Timestamp = (pd.Timestamp.utcnow() - pd.Timedelta(minutes=1))

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

    # Get and save all sympbols
    df_data = get_latest_ticks(symbols, level, start_datetime, client, logger)

    if df_data is not None and not df_data.empty:
        end_date = df_data.timestamp.dt.date.max()
        df_data.to_csv(
            output_path / f'latest_from_{start_datetime}.csv', index=False
        )


    client.disconnect()
