#!/bin/bash
set -o allexport
source .env
set +o allexport
rsync -r {./,activities,lib}
for thing in activities lib daemon.py repl.py run.sh; do
  rsync -r $thing $REMOTE:$REMOTE_DIR/$dir/
done
rlwrap ssh $REMOTE "cd $REMOTE_DIR; ./run.sh $@"
