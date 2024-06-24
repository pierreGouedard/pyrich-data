#!/bin/bash

# Set paths
set LOCAL_STORE_PATH = ~/pyrich-data/data/xtb/consolidated_data
set REMOTE_BACKUP_PATH = /home/ubuntu/pyrich-data/data/xtb/

# download backup & consolidate data
scp -P 54819 -i ~/.ssh/id_rsa -r -p ubuntu@54.36.191.1:$REMOTE_BACKUP_PATH/events/backup_events.csv $LOCAL_STORE_PATH/tmp_events.csv ; \
scp -P 54819 -i ~/.ssh/id_rsa -r -p ubuntu@54.36.191.1:$REMOTE_BACKUP_PATH/ticks/backup_ticks.csv $LOCAL_STORE_PATH/tmp_ticks.csv ; \
scp -P 54819 -i ~/.ssh/id_rsa -r -p ubuntu@54.36.191.1:$REMOTE_BACKUP_PATH/history/backup_history.csv $LOCAL_STORE_PATH/tmp_history.csv ; \
python python src/scripts/prod/consolidate_data.py


