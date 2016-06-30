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

def lxcservers(hvs, lxcs):
    print hvs
    print lxcs
    srvs = {}
    for lxc in lxcs:
        for i, hst in enumerate(hvs[lxc]):
            if hst.lxc.role not in srvs:
                srvs[hst.lxc.role] = []
            srvs[hst.lxc.role].append(hst.address)
    return srvs

class FilterModule(object):
    def filters(self):
        return {
            'lxcservers': lxcservers,
        }

