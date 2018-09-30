#!/bin/bash
source venv/bin/activate
set -o allexport
source .env
set +o allexport
export PYTHONPATH="$(pwd)/:$PYTHONPATH"
python3 $@
