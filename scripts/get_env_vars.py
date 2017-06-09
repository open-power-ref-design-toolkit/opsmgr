#!/usr/bin/env python
#
# Copyright 2017 IBM US, Inc.
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

"""
Early in the bootstrap process the needed python libraries are not available.
This is really a chicken and egg problem. If invoked from Genesis directly
then any needed variables will already be set so we can safely skip this.
Otherwise, the user will need to manually set any http_proxy settings.
"""

import argparse
import signal
import sys
try:
    import yaml
except Exception:
    sys.stderr.write("Environment variables not set. Python libraries are "
                     "not available.\n")
    sys.exit(1)


def _load_yml(inventory_name):
    with open(inventory_name, 'r') as stream:
        try:
            gen_dict = yaml.safe_load(stream)
        except yaml.YAMLError:
            raise
    return gen_dict


def process_inventory(inv_name):
    """Process the input inventory file.

    :param inv_name: The path name of the input genesis inventory.
    """
    gen_dict = _load_yml(inv_name)
    env_vars_dict = gen_dict.get('deployment-environment')
    if env_vars_dict == None or env_vars_dict == {}:
        print 'deployment_environment_variables: {}'
    else:
        print 'deployment_environment_variables:'
        for k in env_vars_dict:
            print '    ' + k + ': "' + env_vars_dict[k] + '"'


def parse_command():
    """Parse the command arguments for generate user config."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('A command to retrieve the environment variables'
                     ' based on the Genesis inventory YAML file.'))
    parser.add_argument('-i', '--input-file', required=True,
                        help=('Path to the Genesis inventory YAML file'))

    parser.set_defaults(func=process_inventory)
    return parser


def signal_handler(signal, frame):
    """Signal handler to for processing, e.g. keyboard interrupt signals."""
    sys.exit(0)


def main():
    """Main function."""
    signal.signal(signal.SIGINT, signal_handler)
    parser = parse_command()
    args = parser.parse_args()
    signal.signal(signal.SIGINT, signal_handler)

    if (len(sys.argv) < 1):
        parser.print_help()
        sys.exit(1)

    args.func(args.input_file)

    return 0


if __name__ == "__main__":
    main()
