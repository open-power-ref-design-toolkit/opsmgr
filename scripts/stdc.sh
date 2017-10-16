#!/bin/bash
source $(dirname $0)/env.sh
pushd ${OPSMGR_DIR}
#The following sets OPSMGR_RECIPE to a
#value if it is not set
: ${OPSMGR_RECIPE:=osa-newton}

echo OPSMGR_RECIPE=$OPSMGR_RECIPE
echo OPSMGR_PRL=$OPSMGR_PRL

# opsmgr bootstrap sequence
# please run from opsmgr root directory

# performs any OpsMgr bootstrap setup 
if [[ ! -z $OPSMGR_RECIPE ]]; then
    export OPSMGR_PRL=../recipes/${OPSMGR_RECIPE}
    echo OPSMGR_PRL=$OPSMGR_PRL
fi

echo "from recipes running setup.yml"
pushd recipes

if [[ -e $OPSMGR_PRL/inventory ]]; then

    ansible-playbook -e "opsmgr_lib=../lib" -i $OPSMGR_PRL/inventory setup.yml
    rc=$?
    if [ $rc != 0 ]; then
        echo "Failed running opsmgr recipes/setup.yml, rc=$rc"
        exit 2
    fi
else
    echo "Unable to run setup.yml -- proceeding"
fi

#updatessh playbook fixes an issue with SSH timing out
ansible-playbook updatessh.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed to update /etc/ssh/sshd_config and/or /etc/ssh/ssh_config, rc=$rc"
    exit 3
fi

popd

popd
