#!/bin/bash

source $(dirname $0)/env.sh

pushd ${OPSMGR_DIR}
echo "find . -name ".facts" -print | xargs -i rm -rf {}"
echo "find . -name "*~" -print | xargs -i rm -rf {}"
rm -rf ext
rm -rf predeploy/osa/ext
popd

