#!/bin/bash
set -o allexport
source .env
set +o allexport

# ensures we don't deploy old versions of dynamic data
./reploy.sh

rsync -rv *.{py,db,pickle,sh,cookies} .env requirements.txt activities lib c food_club tools $REMOTE:$REMOTE_DIR/$dir/
