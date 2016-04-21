# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import pdb
class Resource(object):
    # The class "constructor" - It's actually an initializer 
    def __init__(self, device):
        self.id = device['deviceid']
        self.name = device['label']
        self.type = device['device-type']
        self.rackLoc = device['rack-eia-location']
        self.userid = device['userid']
        self.mtm = device['machine-type-model']
        self.sn = device['serial-number']
        self.mgmtIpaV4 = device['ip-address']
        self.hostname = device['hostname']
        self.version = device['version']
        self.web_url = device['web_url']
        self.deviceId = device['deviceid']
    
        # displayable host / ip address info
        if ((self.hostname != None) and (self.mgmtIpaV4 != None)):
           # both pieces of info are set.
           self.displayHost = self.hostname + " (" + self.mgmtIpaV4 + ")"
        elif (self.mgmtIpaV4 != None):
           # only ip address field is set
           self.displayHost = self.mgmtIpV4 + " (" + self.mgmtIpaV4 + ")"
        else:
           # only hostname is set
           self.displayHost = self.hostname
