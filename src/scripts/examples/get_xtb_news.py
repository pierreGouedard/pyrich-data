# Global import
from typing import Any, Tuple
from pathlib import Path
import logging
import sys
import os

import pandas as pd
from dotenv import load_dotenv

project_path = Path(__file__).parents[3]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xapi_core import APIClient
from src.core.xapi_utils import init_api_client


def get_news_data(
        client: APIClient, start_date, logger: logging.Logger
) -> Tuple[pd.DataFrame, Any, Any]:

    # Pandas timestmanp are seconds UNIX timestamp, API is milliseconds UNIX timestamp, hence factor 1e3 in "start"
    args = {
        "start": int(pd.Timestamp(start_date).timestamp() * 1e3),
        "end": 0
    }
    resp = client.commandExecute('getNews', arguments=args)
    if resp['status']:
        df_data = (
            pd.DataFrame(resp['returnData'])
            .assign(
                timestamp=lambda x: pd.to_datetime(x.time, unit='ms', origin='unix'),

            )
            .sort_values(by='timestamp')
            .loc[:, ['timestamp', 'title', 'body', 'bodylen']]
        )

        # Log success
        start, end = df_data.timestamp.min().date(), df_data.timestamp.max().date(),
        logger.info(f"""Successfully fetch news data covering {start} - {end})""")

        return df_data, start, end


if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data"
    output_path = data_path / 'xtb' / 'examples' / 'news'

    # Parameters
    env_filename = '.env'
    start_date = '2024-05-26'

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
    df_data, start, end = get_news_data(client, start_date, logger)
    client.disconnect()

    if df_data is not None:
        df_data.to_csv(
            output_path / f'news_{start}_{end}.csv', index=False
        )

