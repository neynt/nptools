#!/bin/bash
trap 'trap - SIGTERM && kill -- -$$' SIGINT SIGTERM EXIT
tail -f -c 0 daemon.log &
./run.sh -u $@ daemon.py >> daemon.log
