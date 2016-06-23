#!/bin/bash

source $(dirname $0)/env.sh

pushd ${OPSMGR_DIR}
echo "find . -name ".facts" -print | xargs -i rm -rf {}"
echo "find . -name "*~" -print | xargs -i rm -rf {}"
pushd ext
if [[ $(basename `pwd`) = ext ]]
then
echo "rm -f *"
echo "rm -f .spec"
fi
popd
popd

