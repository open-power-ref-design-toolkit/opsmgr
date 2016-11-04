Recipe: PrivateCloud-Mitaka
=================================

This is a recipe to generate an OpsMgr profile to install it on a Private Cloud cluster.
In this scenario we assume the following components exist::

   * Genesis (for bare metal installation)
   * OS-Services, istalls OpenStack-Ansible on OpenPOWER nodes

Once this playbook runs you can call the OpsMgr main playbooks by modifying the value of
the OPSMGR_PRL environment variable to point to the generated "profile" directory.
The OPSMGR_PRL variable uses a path relative to the playbooks directory. Example::

   > export OPSMGR_PRL=../recipes/privatecloud-mitaka/profile

And then run both the main OpsMgr playbooks. Rxample::

   > cd ../../playbooks
   > ansible-playbook -e "OPSMGR_LIB=../lib" -i $OPSMGR_PRL/inventory <playbook_name>

Please consult the README in the playbooks directory for more informatin on how to
install OpsMgr.

