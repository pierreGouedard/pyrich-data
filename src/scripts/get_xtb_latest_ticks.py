# Global import
from typing import List
from pathlib import Path
import logging
import sys
import os

import pandas as pd
from dotenv import load_dotenv

project_path = Path(__file__).parents[2]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xApi_core import APIClient
from src.core.xApi_utils import init_api_client

# TODO: create arg parser
#   use the correct symbol yaml file
#   append files (1 file per day / week / month ?)
#   timestamp logic ?


def get_latest_ticks(
        symbols: List[str], level: int, start_datetime: pd.Timestamp, client: APIClient,
        logger: logging.Logger
) -> pd.DataFrame:

    # Pandas timestmanp are seconds UNIX timestamp, API is milliseconds UNIX timestamp, hence factor 1e3 in "start"
    args = {
        "level": level,
        "timestamp": int(start_datetime.timestamp() * 1e3),
        "symbols": symbols
    }

    # get data from server
    resp = client.commandExecute('getTickPrices', arguments=args)

    # Format data if any
    if resp['status']:
        l_expected_cols = [
            'symbol', 'timestamp', 'ask', 'bid', 'high', 'low', 'askVolume', 'bidVolume',
            "spreadRaw",  "spreadTable"
        ]
        df_data = (
            pd.DataFrame(resp['returnData']['quotations'])
            .assign(timestamp=lambda x: pd.to_datetime(x.timestamp, unit='ms', origin='unix'))
            .loc[:, l_expected_cols]
            .sort_values(by='timestamp')
        )

        # Log success
        logger.info(f"""Successfully fetch ticks for {list(df_data.symbol.unique())}""")
        return df_data


if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data"
    output_path = data_path / 'xtb' / 'ticks'

    # Parameters
    env_filename = '.env'
    symbols = ['AI.FR_9', 'BAYN.DE_9']
    level = 0
    # Todo: either spec by hand or keep last minutes timestamp?
    start_datetime = pd.Timestamp('2024-06-04 10:00:00')

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

    if df_data is not None:
        end_date = df_data.timestamp.dt.date.max()
        df_data.to_csv(
            output_path / f'latest_from_{start_datetime}.csv', index=False
        )


    client.disconnect()
