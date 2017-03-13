#!/usr/bin/python

# Copyright 2016,2017 IBM US, Inc.
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


# Script to parse variables with '-' in the them which ansinble doesn't support
# Those variables are defined in /var/oprc/inventory.yml

# Usage ./inventory_parse <variable name>

import sys
import yaml

INVENTORY_FILE = "/var/oprc/inventory.yml"

def _load_yml():
    with open(INVENTORY_FILE, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as ex:
            print(ex)
            sys.exit(1)

def main():
    if len(sys.argv) !=2:
        print("Usage: ./inventory_parse <variable name>")
        exit(1)

    inventory = _load_yml();
    value = inventory[sys.argv[1]]
    print(value)

if __name__ == "__main__":
    main()
