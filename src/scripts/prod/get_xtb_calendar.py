# Global import
from pathlib import Path
import logging
import sys
import yaml
import os

import pandas as pd
from dotenv import load_dotenv

project_path = Path(__file__).parents[3]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xApi_utils import init_api_client, get_calendar_data
from src.core.xtbdata_utils import merge_calendar_data


if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data"
    calendar_path = data_path / 'xtb' / 'events'

    # Parameters
    env_filename = '.env'

    # Load backup config
    backup_period = yaml.safe_load((project_path / 'config' / 'backup.yaml').open('r'))['events']

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
    df_events, start, end = get_calendar_data(client, logger)
    client.disconnect()

    # Load current event dataframe, merge new events
    if (calendar_path / 'events.csv').exists():
        df_prev_events = pd.read_csv(calendar_path / 'events.csv')
    else:
        df_prev_events = None
    df_events = merge_calendar_data(df_events, df_prev_events)

    #  if backup period is met (oldest data older than today - backup period) save a copy of file with prefix
    #  'backup_'
    datetime_backup_limit = pd.Timestamp.utcnow().tz_convert(None) - pd.Timedelta(**backup_period)
    if df_events.timestamp.min() < datetime_backup_limit:
        df_events.to_csv(calendar_path / 'backup_events.csv', index=False)
        os.remove(calendar_path / "events.csv")
    else:

        df_events.to_csv(calendar_path / 'events.csv', index=False)


