#!/bin/bash
set -o allexport
source .env
set +o allexport

python3 daemon.py 2>&1
