# Global import
from pathlib import Path
import logging
import sys
import os

from dotenv import load_dotenv

project_path = Path(__file__).parents[3]
sys.path.append(project_path.as_posix())

# Local import
from src.core.xapi_utils import init_api_client, get_profit


if __name__ == '__main__':

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
    get_profit(client, logger)
    client.disconnect()
