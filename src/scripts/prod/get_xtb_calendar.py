# Global import
from pathlib import Path
import sys
import yaml
import os

import pandas as pd
from dotenv import load_dotenv

project_path = Path(__file__).parents[3]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xapi_utils import init_api_client, get_calendar_data
from src.core.dev_utils import set_up_logger


if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data"
    log_dir = project_path / 'logs'
    calendar_path = data_path / 'xtb' / 'events'

    # Parameters
    env_filename = '.env'
    curr_date = pd.Timestamp.utcnow().floor('D')

    # Load backup config
    backup_period = yaml.safe_load((project_path / 'config' / 'backup.yaml').open('r'))['events']

    # Load env
    dotenv_path = project_path / env_filename
    load_dotenv(dotenv_path)

    # logger properties
    logger = set_up_logger('event_collection', log_dir)

    # Create & connect to RR socket
    client, ssid = init_api_client(
        {
            'HOST': os.environ['HOST'], 'PORT': os.environ['PORT'],
            'USER_ID': os.environ['USER_ID'], 'PASSWORD': os.environ['PASSWORD']
        },
        logger
    )

    # Get minute graph data for a particular symbol
    df_events, _, _ = get_calendar_data(client, logger)
    client.disconnect()

    # Log ticks download failure
    if df_events is None:
        raise RuntimeError('no event returned')
    elif df_events.empty:
        raise RuntimeError('no event returned')

    # Save ticks
    df_events.to_csv(calendar_path / f'events_{curr_date}.csv', index=False)
