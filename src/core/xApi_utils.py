# Global import
from typing import Tuple, Dict, List, Any
import logging

import pandas as pd

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
    login_response = client.execute(loginCommand(
        userId=connect_kwargs['USER_ID'], password=connect_kwargs['PASSWORD'],
    ))

    if login_response['status'] == False:
        logger.info('Login failed. Error code: {0}'.format(login_response['errorCode']))
        return None, None

    return client, login_response['streamSessionId']


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

        if len(resp['returnData']['quotations']) > 0:
            df_data = (
                pd.DataFrame(resp['returnData']['quotations'])
                .assign(timestamp=lambda x: pd.to_datetime(x.timestamp, unit='ms', origin='unix'))
                .loc[:, l_expected_cols]
                .sort_values(by='timestamp')
            )
            logger.info(f"""Successfully fetch ticks for {list(df_data.symbol.unique())}""")

        else:
            df_data = pd.DataFrame(columns=l_expected_cols)
            logger.warning(f"No history data returned for {symbols}, start datetime requested {start_datetime}")

        return df_data

    # Log failure
    logger.warning(f"error during history download: {resp}")


def get_historical_data(
        symbol: str, period: int, start_date: pd.Timestamp, client: APIClient, logger: logging.Logger
) -> pd.DataFrame:

    # Pandas timestamp are seconds UNIX timestamp, API is milliseconds UNIX timestamp,
    # hence factor 1e3 in "start"
    args = {
        "info": {
            "period": period,
            "start": int(start_date.timestamp() * 1e3),
            "symbol": symbol
        }
    }

    # get data from server
    resp = client.commandExecute('getChartLastRequest', arguments=args)

    # Format data if any
    if resp['status']:
        l_cols = ['timestamp', 'open', 'high', 'low', 'close', 'vol']
        nb_decimal = int(resp['returnData']['digits'])
        if len(resp['returnData']['rateInfos']) > 0:
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
            logger.info(f"""
            Successfully fetch data for {symbol} (period {d_period_mapping[period]} - start {start_date})
            """)

        else:
            df_data = pd.DataFrame(columns=l_cols)
            logger.warning(f"No history data returned for {symbol}, start date requested {start_date}")

        return df_data

    # Loag failure
    logger.warning(f"error during history download: {resp}")


def get_profit(
        client: APIClient, logger: logging.Logger
) -> pd.DataFrame:
    # TODO: to complete
    # Pandas timestmanp are seconds UNIX timestamp, API is milliseconds UNIX timestamp, hence factor 1e3 in "start"
    args = {
        "closePrice": 1.1000,
        "cmd": 1,
        "openPrice": 1.2233,
        "symbol": "EURPLN",
        "volume": 20.0
    }

    # get data from server
    resp = client.commandExecute('getProfitCalculation', arguments=args)

    # Format data if any
    if resp['status']:
        return


def get_calendar_data(
        client: APIClient, logger: logging.Logger
) -> Tuple[pd.DataFrame, Any, Any]:

    resp = client.commandExecute('getCalendar')
    if resp['status']:
        df_data = (
            pd.DataFrame(resp['returnData'])
            .assign(timestamp=lambda x: pd.to_datetime(x.time, unit='ms', origin='unix').dt.floor('h'))
            .sort_values(by='timestamp')
            .loc[:, ['timestamp', 'country', 'title', 'current', 'previous', 'forecast', 'impact', 'period']]
        )

        # Log success
        start, end = df_data.timestamp.min().date(), df_data.timestamp.max().date(),
        logger.info(f"""
        Successfully fetch calendar data covering {start} - {end})
        """)

        return df_data, start, end
