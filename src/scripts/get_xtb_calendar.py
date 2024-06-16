# Global import
from typing import Any, Tuple
from pathlib import Path
import argparse
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


def get_calendar_data(
        client: APIClient, logger: logging.Logger
) -> Tuple[pd.DataFrame, Any, Any]:

    resp = client.commandExecute('getCalendar')
    if resp['status']:
        df_data = (
            pd.DataFrame(resp['returnData'])
            .assign(
                timestamp=lambda x: pd.to_datetime(x.time, unit='ms', origin='unix'),

            )
            .sort_values(by='timestamp')
            .loc[:, ['timestamp', 'title', 'current', 'previous', 'forecast', 'impact', 'period']]
        )

        # Log success
        start, end = df_data.timestamp.min().date(), df_data.timestamp.max().date(),
        logger.info(f"""
        Successfully fetch calendar data covering {start} - {end})
        """)

        return df_data, start, end


if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data"
    output_path = data_path / 'xtb' / 'events'

    # Parameters
    env_filename = '.env'

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
    df_data, start, end = get_calendar_data(client, logger)
    client.disconnect()

    if df_data is not None:
        end_date = df_data.timestamp.dt.date.max()
        df_data.to_csv(
            output_path / f'calendar_{start}_{end}.csv', index=False
        )

