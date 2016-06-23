#!/bin/bash

if [[ "$0" = /* ]]
then
RELPATH=$(dirname $0)/..
else
RELPATH=${PWD}/$(dirname $0)/..
fi

export OPSMGR_DIR=$(readlink -f ${RELPATH})

