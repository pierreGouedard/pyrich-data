# Global import
from pathlib import Path
import logging
import sys
import os

from dotenv import load_dotenv

project_path = Path(__file__).parents[3]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xApi_utils import init_api_client, get_calendar_data


if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data"
    output_path = data_path / 'xtb' / 'examples' / 'events'

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

