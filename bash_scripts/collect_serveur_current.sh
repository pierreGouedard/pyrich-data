#!/bin/bash
# TODO: make a script that scp back the server data collection backup and store it in local path

set LOCAL_STORE_PATH = ~/pyrich-data/data/xtb/consolidated_data
set REMOTE_BACKUP_PATH = /home/ubuntu/pyrich-data/data/xtb/

# download backup
scp -P 54819 -i .ssh/id_rsa -r -p ubuntu@54.36.191.1:{$LOCAL_STORE_PATH}/events/backup_events.csv $LOCAL_STORE_PATH
scp -P 54819 -i .ssh/id_rsa -r -p ubuntu@54.36.191.1:{$LOCAL_STORE_PATH}/ticks/backup_ticks.csv $LOCAL_STORE_PATH
scp -P 54819 -i .ssh/id_rsa -r -p ubuntu@54.36.191.1:{$LOCAL_STORE_PATH}/history/backup_history.csv $LOCAL_STORE_PATH
