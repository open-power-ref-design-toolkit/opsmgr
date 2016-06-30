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

def updatelxc(lxcs, host, lxc_info):
    print lxc_info
    for i, res in enumerate(lxc_info['results']):
        for j, lxc in enumerate(lxcs):
            if ('address' not in lxc) and (res['item']['name'] == lxc['name']):
                lxc.update({'address': res['lxc_container']['ips'][0], 'host': host})
                break
    return lxcs

class FilterModule(object):
    def filters(self):
        return {
            'updatelxc': updatelxc,
        }

