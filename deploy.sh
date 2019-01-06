#!/bin/bash
set -o allexport
source .env
set +o allexport
rsync -rv *.{py,db,pickle,sh,cookies} .env activities lib c food_club tools $REMOTE:$REMOTE_DIR/$dir/
