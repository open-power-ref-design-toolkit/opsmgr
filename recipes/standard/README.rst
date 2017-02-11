Recipe: Standard
========================

Use this recipe to generate an OpsMgr profile to install in a non OpenStack environment
without the OpsMgr Horizon Graphical User Interface Extension

Example::

   > ./run.sh

Once this playbook runs you can call the OpsMgr main playbooks by modifying the value of
the OPSMGR_RECIPE variable to reference this recipe. Example::

   > export OPSMGR_RECIPE=standard

And then run the main OpsMgr playbooks. Example::

   > cd ../../playbooks
   > export OPSMGR_DIR=`pwd`/..
   > export OPSMGR_PRL=$OPSMGR_DIR/recipes/$OPSMGR_RECIPE/profile
   > ansible-playbook -e "opsmgr_dir=$OPSMGR_DIR" -i $OPSMGR_PRL/inventory <playbook_name>

Please consult the README in the playbooks directory for more information on how to
install OpsMgr.
