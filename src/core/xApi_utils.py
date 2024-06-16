# Global import
from typing import Tuple, Dict
import logging

# Local import
from src.core.xApi_core import APIClient, loginCommand


d_period_mapping = {
    1: 'M1', 5: 'M5', 15: 'M15', 30: 'M30', 60: 'H1', 240: "H4", 1440: 'D1', 10080: 'W1', 43200: 'm1'
}


def init_api_client(
        connect_kwargs: Dict[str, str], logger: logging.Logger
) -> Tuple[APIClient, str]:
    # create & connect to RR socket
    client = APIClient(
        address=connect_kwargs['HOST'],
        port=int(connect_kwargs['PORT']),
        logger=logger
    )
    # connect to RR socket, login

    import IPython
    IPython.embed()
    login_response = client.execute(loginCommand(
        userId=connect_kwargs['USER_ID'], password=connect_kwargs['PASSWORD'],
    ))

    if login_response['status'] == False:
        logger.info('Login failed. Error code: {0}'.format(login_response['errorCode']))
        return None, None

    return client, login_response['streamSessionId']