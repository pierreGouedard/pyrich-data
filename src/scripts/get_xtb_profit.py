# Global import
from pathlib import Path
import logging
import sys
import os

import pandas as pd
from dotenv import load_dotenv

project_path = Path(__file__).parents[4]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xApi_core import APIClient
from src.core.xApi_utils import init_api_client


def get_profit(
        client: APIClient, logger: logging.Logger
) -> pd.DataFrame:

    # Pandas timestmanp are seconds UNIX timestamp, API is milliseconds UNIX timestamp, hence factor 1e3 in "start"
    args = {
        "closePrice": 1.1000,
        "cmd": 1,
        "openPrice": 1.2233,
        "symbol": "EURPLN",
        "volume": 20.0
    }

    # get data from server
    resp = client.commandExecute('getProfitCalculation', arguments=args)

    # Format data if any
    if resp['status']:
        return


if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data"
    output_path = data_path / 'xtb' / 'ticks'

    # Parameters
    env_filename = '.env'
    symbol = 'AI.FR_9'
    close_price = 0
    open_price = 0
    volume = 1
    cmd = 0

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
    df_data = get_profit(client, logger)
    client.disconnect()
