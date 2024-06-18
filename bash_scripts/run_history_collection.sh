#!/bin/bash
# Init conda
source ~/miniconda3/etc/profile.d/conda.sh

# Activate conda env
conda activate pyrich-env

# Run script
python pyrich-data/src/scripts/prod/get_xtb_history_data.py