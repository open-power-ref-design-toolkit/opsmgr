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

def getaddress(address_pool, used_pool):
    for i, addr in enumerate(address_pool):
        if addr not in used_pool:
            used_pool.append(addr)
            return addr
    return None

class FilterModule(object):
    def filters(self):
        return {
            'getaddress': getaddress,
        }

