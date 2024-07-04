# Global import
from pathlib import Path
import yaml
import sys
import os

from pandas import Timedelta, Timestamp
from dotenv import load_dotenv
from pandas._libs.tslibs.parsing import DateParseError

project_path = Path(__file__).parents[3]
sys.path.append(project_path.as_posix())

# Local import
from src.core.dev_utils import set_up_logger


if __name__ == '__main__':
    # Get paths
    xtb_path = project_path / "data" / 'xtb'
    log_dir = project_path / 'logs'

    # Load backup config
    backup_period = yaml.safe_load((project_path / 'config' / 'backup.yaml').open('r'))

    # Set up logger
    logger = set_up_logger('file_cleaner', log_dir)

    for key in ['ticks', 'history', 'events']:
        limit_date = (Timestamp.utcnow() - Timedelta(**backup_period[key]))
        for filename in os.listdir(xtb_path / key):

            # Keu should be in filename
            if key not in filename:
                continue

            # Try to read file date in filename
            try:
                filedate_str = filename.split('_')[-1].split('.csv')[0]
                filedate = Timestamp(filedate_str)
            except DateParseError:
                logger.info(f'DateParseError: {filedate_str}')
                continue

            # If too old, remove file
            if filedate < limit_date:
                os.remove(xtb_path / key / filename)
                logger.info(f'Removing file: {xtb_path / key / filename}')
