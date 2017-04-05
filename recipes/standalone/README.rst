Recipe: OpsMgr Standalone
=================================

This is a recipe to generate an OpsMgr profile to install it on a standalone cluster.
It can be used for other recipes that only need basic HW+OS monitoring capabilities.
In this scenario we assume the following components exist::

   * Genesis (for bare metal installation)

This playbook orchestrates the OpsMgr main playbooks by modifying the value of
the OPSMGR_PRL environment variable to point to the generated "profile" directory.
The OPSMGR_PRL variable uses a path relative to the playbooks directory. Example::

   > export OPSMGR_PRL=../recipes/standalone/profile

To properly deploy this recipe please run the following scripts in sequence::

   > bootstrap-prereq.sh
   > bootstrap-opsmgr.sh
   > provision-prereq.sh
   > provision-opsmgr.sh

Please consult the README in the playbooks directory for more informatin on how to
install OpsMgr.

