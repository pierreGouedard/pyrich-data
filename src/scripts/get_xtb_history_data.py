# Global import
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
from src.core.xApi_utils import init_api_client, d_period_mapping


def get_historical_data(
        symbol: str, period: int, start_date: str, client: APIClient, logger: logging.Logger
) -> pd.DataFrame:

    # Pandas timestmanp are seconds UNIX timestamp, API is milliseconds UNIX timestamp, hence factor 1e3 in "start"
    args = {
        "info": {
            "period": period,
            "start": int(pd.Timestamp(start_date).timestamp() * 1e3),
            "symbol": symbol
        }
    }

    # get data from server
    resp = client.commandExecute('getChartLastRequest', arguments=args)

    # Format data if any
    if resp['status']:
        nb_decimal = int(resp['returnData']['digits'])
        df_data = (
            pd.DataFrame(resp['returnData']['rateInfos'])
            .assign(
                timestamp=lambda x: pd.to_datetime(x.ctm, unit='ms', origin='unix'),
                open=lambda x: x.open / pow(10, nb_decimal),
                high=lambda x: x.high / pow(10, nb_decimal),
                low=lambda x: x.low / pow(10, nb_decimal),
                close=lambda x: x.close / pow(10, nb_decimal),
            )
            .loc[:, ['timestamp', 'open', 'high', 'low', 'close', 'vol']]
            .sort_values(by='timestamp')
        )

        # Log success
        logger.info(f"""
        Successfully fetch data for {symbol} (period {d_period_mapping[period]} - \
        start {start_date})
        """)
        return df_data


if __name__ == '__main__':
    # Get paths
    data_path = project_path / "data"
    output_path = data_path / 'xtb' / 'history'

    # Parameters
    env_filename = '.env'
    symbol = 'AI.FR_9'
    period = 1
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
    df_data = get_historical_data(symbol, period, start_date, client, logger)
    client.disconnect()

    if df_data is not None:
        end_date = df_data.timestamp.dt.date.max()
        df_data.to_csv(
            output_path / f'{symbol}_{d_period_mapping[period]}_{start_date}_{end_date}.csv', index=False
        )

