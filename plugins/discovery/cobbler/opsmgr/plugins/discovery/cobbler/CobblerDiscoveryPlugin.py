# Copyright 2016, IBM US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import spur
from opsmgr.common import exceptions
from opsmgr.common.utils import entry_exit
from opsmgr.inventory.resource_mgr import add_resource, validate_address, validate_label
from opsmgr.discovery.interfaces.IDiscoveryPlugin import IDiscoveryPlugin

COBBLER_CMD_SYSTEM_LIST = "cobbler system list"
COBBLER_CMD_SYSTEM_DUMPVARS = "cobbler system dumpvars --name"
COBBLER_TAG_MAC = "mac_address_eth0"
COBBLER_TAG_ADDRESS = "ip_address_eth0"
COBBLER_TAG_BREED = "breed"

COBBLER_DIC_TYPES = {'ubuntu': 'Ubuntu',
                     'rhel': 'Redhat Enterprise Linux'}

# TODO: read these parameters from Cobbler too
SUDO_PASSWORD = "setup4me"
DEFAULT_RESOURCE_USER = "ubuntu"
DEFAULT_RESOURCE_PWD = "ubuntu"


class CobblerPlugin(IDiscoveryPlugin):

    def __init__(self):
        self.shell = None

    @staticmethod
    def get_type():
        return "Cobbler"

    @entry_exit(exclude_index=[], exclude_name=[])
    def list_systems(self):
        """ Method to query Cobbler and list all systems defined within its database
        """
        _method_ = "CobblerDiscoveryPlugin.list_systems"
        systems = []
        if self.shell is None:
            self.shell = spur.LocalShell()
        with self.shell:
            try:
                process = self.shell.spawn(["sh", "-c", "sudo -S %s" % COBBLER_CMD_SYSTEM_LIST])
                process.stdin_write(SUDO_PASSWORD + "\n")
                result = process.wait_for_result()
                # iterate through output if command executed successfully
                if result.return_code == 0:
                    for line in result.output.decode('ascii').splitlines():
                        system = line.strip()
                        systems.append(system)
                        logging.info("%s::Found system to be imported from Cobbler::%s", _method_, system)
                else:
                    logging.error("%s::Failed to retrieve systems from Cobbler", _method_)
            except (spur.ssh.NoSuchCommandError, spur.ssh.ConnectionError) as e:
                logging.exception(e)
                logging.error("%s::Connection error - host = %s", _method_, self.shell._hostname)
                raise exceptions.ConnectionException(e)
        return systems

    def format_resource(self, label, rtype, address, user):
        return "Resource[label=%s,type=%s,address=%s,user=%s]" % (label, rtype, address, user)

    @entry_exit(exclude_index=[], exclude_name=[])
    def find_resources(self):
        self.discover_resources(resource_label='*', offline=True, add=False)

    @entry_exit(exclude_index=[], exclude_name=[])
    def import_resources(self, resource_label='*', offline=False):
        self.discover_resources(resource_label, offline, add=True)

    @entry_exit(exclude_index=[], exclude_name=[])
    def discover_resources(self, resource_label='*', offline=False, add=False):
        """ Method to query all data from all systems defined within Cobbler's database
        """
        _method_ = "CobblerDiscoveryPlugin.import_resources"
        systems = self.list_systems()
        if self.shell is None:
            self.shell = spur.LocalShell()
        for system in systems:
            if resource_label != '*' and resource_label != system:
                continue
            with self.shell:
                try:
                    process = self.shell.spawn(["sh", "-c", "sudo -S %s %s" % (COBBLER_CMD_SYSTEM_DUMPVARS, system)])
                    process.stdin_write(SUDO_PASSWORD + "\n")
                    result = process.wait_for_result()
                    resource_ipv4 = None
                    resource_breed = None
                    # iterate through output if command executed successfully
                    if result.return_code == 0:
                        for line in result.output.decode('ascii').splitlines():
                            # Parse the output to extract the resource data
                            if COBBLER_TAG_ADDRESS in line:
                                resource_ipv4 = line.split(':')[1].strip()
                            elif COBBLER_TAG_BREED in line:
                                resource_breed = line.split(':')[1].strip()
                    else:
                        logging.error("%s::Failed to import data from Cobbler for system::%s", _method_, system)
                    # Figure out if there is a valid resource type for this system
                    resource_type = COBBLER_DIC_TYPES[resource_breed]
                    resource = self.format_resource(system, resource_type, resource_ipv4, DEFAULT_RESOURCE_USER)
                    if resource_type is None:
                        print("Warning:: Cannot find a suitable resource type for %s" % resource)
                    else:
                        print("Discovered from %s: %s" % (self.get_type(), resource))
                        rc1, message = validate_label(system)
                        if rc1 != 0:
                            print("Warning:: %s" % message)
                        rc2, message = validate_address(resource_ipv4)
                        if rc2 != 0:
                            print("Warning:: %s" % message)
                        if add:
                            if rc1 == 0 and rc2 == 0:
                                rc, message = add_resource(system, resource_type, resource_ipv4,
                                                           DEFAULT_RESOURCE_USER, DEFAULT_RESOURCE_PWD,
                                                           offline=offline)
                                if rc == 0:
                                    print("Resource imported: %s" % system)
                                else:
                                    print("Import error: %s" % message)
                            else:
                                print("Cannot import: %s - conflicting resource exists" % system)
                except (spur.ssh.NoSuchCommandError, spur.ssh.ConnectionError) as e:
                    logging.exception(e)
                    logging.error("%s::Connection error - host = %s", _method_, self.shell._hostname)
                    raise exceptions.ConnectionException(e)

    @entry_exit(exclude_index=[3, 4], exclude_name=["pwd", "pkey"])
    def connect(self, host, user, pwd, pkey=None):
        """ Method to optionally connecting to a remote host prior to interacting
            with Cobbler
        """
        _method_ = "connect"
        if pkey:
            self.shell = spur.SshShell(hostname=host, username=user, private_key_file=pkey,
                                       missing_host_key=spur.ssh.MissingHostKey.accept)
        else:
            self.shell = spur.SshShell(hostname=host, username=user, password=pwd)
        with self.shell:
            try:
                self.shell.run(["echo", "-n", "ping"])
            except (spur.ssh.NoSuchCommandError, spur.ssh.ConnectionError) as e:
                logging.exception(e)
                logging.error("%s::Connection error - host = %s", _method_, host)
                raise exceptions.ConnectionException(e)

    @entry_exit(exclude_index=[], exclude_name=[])
    def disconnect(self):
        """ Method to disconnect from a previously connected remote host
        """
        if self.shell:
            self.shell.close()
            self.shell = None
