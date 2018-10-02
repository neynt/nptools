#!/bin/bash
set -o allexport
source .env
set +o allexport
for dir in ./ activities lib; do
  rsync -r $dir/*.py $REMOTE:$REMOTE_DIR/$dir/
done
rlwrap ssh $REMOTE "cd $REMOTE_DIR; ./run.sh $@"
