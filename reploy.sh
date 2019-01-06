#!/bin/bash
set -o allexport
source .env
set +o allexport
rsync -rv $REMOTE:$REMOTE_DIR/$dir/{*.{db,pickle,cookies},food_club} .
