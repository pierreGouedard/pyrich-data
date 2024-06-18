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
from src.core.xapi_core import APIClient
from src.core.xapi_utils import init_api_client


def get_and_format_symbols(client: APIClient, output_path: Path, logger: logging.Logger) -> None:

    # second method of invoking commands
    resp = client.commandExecute('getAllSymbols')

    if not resp['status']:
        print('getAllSymbols command failed. Error code: {0}'.format(resp['errorCode']))
        return

    # Format & save Symbols
    df_symbols = pd.DataFrame(resp['returnData'])
    df_symbols.to_csv(output_path)


if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data" / "xtb" / 'examples' / 'utils'

    # Parameters
    env_filename = '.env'
    symbol = ''

    # Load env
    dotenv_path = project_path/ env_filename
    load_dotenv(dotenv_path)

    # logger properties
    logger = logging.getLogger("jsonSocket")
    FORMAT = '[%(asctime)-15s][%(funcName)s:%(lineno)d] %(message)s'
    logging.basicConfig(format=FORMAT)

    # Create & connect to RR socket
    client, ssid = init_api_client(
        {
            'HOST': os.environ['HOST'], 'PORT': os.environ['PORT'],
            'USER_ID': os.environ['USER_ID'], 'PASSWORD': os.environ['PASSWORD']
        },
        logger
    )

    # Get and save all sympbols
    get_and_format_symbols(client, data_path / 'xtb_symbols.csv', logger)
    client.disconnect()
