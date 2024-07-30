#!/bin/bash

LOCAL_STORE_PATH=~/pyrich-projects/pyrich-data/data/xtb/consolidated_data
REMOTE_BACKUP_PATH=/home/ubuntu/pyrich-data/data/xtb

# download backup & consolidate data
scp -P 54819 -i ~/.ssh/id_rsa -r -p ubuntu@54.36.191.1:$REMOTE_BACKUP_PATH/events/*.csv $LOCAL_STORE_PATH/tmp_events ; \
scp -P 54819 -i ~/.ssh/id_rsa -r -p ubuntu@54.36.191.1:$REMOTE_BACKUP_PATH/ticks/*.csv $LOCAL_STORE_PATH/tmp_ticks ; \
scp -P 54819 -i ~/.ssh/id_rsa -r -p ubuntu@54.36.191.1:$REMOTE_BACKUP_PATH/history/*.csv $LOCAL_STORE_PATH/tmp_history ; \
python src/scripts/prod/consolidate_data.py
