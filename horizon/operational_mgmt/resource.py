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


class Resource(object):
    # The class "constructor" - It's actually an initializer
    def __init__(self, resource):
        self.id = resource['resourceid']
        self.name = resource['label']
        self.type = resource['resource-type']
        self.arch = resource['architecture']
        self.rack_loc = resource['rack-eia-location']
        self.userid = resource['userid']
        self.mtm = resource['machine-type-model']
        self.serial_num = resource['serial-number']
        self.ip_address = resource['ip-address']
        self.hostname = resource['hostname']
        self.version = resource['version']
        self.web_url = resource['web_url']
        self.resource_id = resource['resourceid']

        # displayable host / ip address info
        self.host_name = []
        if (self.hostname is not None) and (self.ip_address is not None):
            # both pieces of info are set.
            self.host_name.append(self.hostname)
            self.host_name.append("(" + self.ip_address + ")")
        elif self.ip_address is not None:
            # only ip address field is set
            self.host_name.append(self.ip_address)
            self.host_name.append("(" + self.ip_address + ")")
        else:
            # only hostname is set
            self.host_name.append(self.hostname)

        # Capabilities
        self.capabilities = []
        for capability in resource['capabilities']:
            self.capabilities.append(capability)
