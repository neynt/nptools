#!/bin/bash
set -o allexport
source .env
set +o allexport
rsync -rv requirements.txt *.py *.sh activities lib $REMOTE:$REMOTE_DIR/$dir/
rlwrap ssh $REMOTE "cd $REMOTE_DIR; ./run.sh $@"
