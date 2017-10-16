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

import functools
import logging
import logging.config
import socket
import subprocess
import yaml

from stevedore import extension

from opsmgr.common import constants


def is_valid_address(address, family=socket.AF_INET):
    # Modified this script to take in any IP address format.
    # This will default to IPv4 if none is specified.
    try:
        socket.inet_pton(family, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False
    return True


def get_strip_strings_array(strings):
    """ takes a comma separated string and returns a list of strings
        using the comma as the delimiter
        example:
            'HMC, V7000 ' -> ['HMC','V7000']

    args:
        strings:   comma separated string list
    returns:
        string[]  list of strings
    """
    string_array = strings.strip()
    string_array = string_array.split(',')
    result = []
    for string in string_array:
        string = string.strip()
        if string:
            result.append(string)
    return result


def execute_command(command):
    """ This function is to execute a command on the local system
        return (rc, stdout, stderr)
    """
    p = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rc = p.wait()
    stdout = []
    stderr = []
    for line in p.stdout.read().decode().splitlines():
        stdout.append(line)
    for line in p.stderr.read().decode().splitlines():
        stderr.append(line)
    p.stdout.close()
    p.stderr.close()
    return (rc, stdout, stderr)


def push_message(message, new_message):
    if new_message is not None and len(new_message) > 0:
        if message:
            message = message + '\n' + new_message
        else:
            message = new_message
    return message


def load_plugin_by_namespace(namespace):
    plugins = {}
    extensions = extension.ExtensionManager(namespace=namespace)

    for ext in extensions:
        plugins[ext.name] = ext.plugin()
    return plugins


def entry_exit(exclude_index=None, exclude_name=None, log_name=None, level=logging.INFO):
    """
    it's a decorator that to add entry and exit log for a function

    input:
    excludeIndex -- the index of params that you don't want to be record
    excludeName -- the name of dictionary params that you don't wnat to be record
    log_name -- name of the log to write the logging to.
    level -- the logging level to log the entry/exit with.  default is INFO level
    """

    def f(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            args_for_print = []
            tmp_index = 0
            arg_len = len(args)
            while tmp_index < arg_len:
                if tmp_index not in exclude_index:
                    args_for_print.append(args[tmp_index])
                tmp_index += 1

            kwargs_for_print = {}
            for a in kwargs:
                if a in exclude_name:
                    continue
                else:
                    kwargs_for_print[a] = kwargs[a]

            logging.getLogger(log_name).log(level,
                                            "%s::Entry params %s %s", func.__name__, "{}".format(
                                                args_for_print), "{}".format(kwargs_for_print))
            result = func(*args, **kwargs)
            logging.getLogger(log_name).log(level,
                                            "%s::Exit %s ", func.__name__, "{}".format(result))
            return result
        return wrapper
    return f


class LoggingService(object):

    @staticmethod
    def _init_logging(file_path, flag=None):
        """
        the function is to init logging by file_path and flag
        the logging configuration file may contain multi config indetified
        using flag as map , so it can be used for different thread
        set flag to None if no flag
        """
        with open(file_path, "rt") as f:
            _config = yaml.load(f)
        if flag == "" or flag is None:
            logging.config.dictConfig(_config)
        else:
            logging.config.dictConfig(_config[flag])

    def init_cli_logging(self):
        try:
            self._init_logging(constants.OPSMGR_LOG_CONF, "cli")
            logging.debug("init_cli_logging loading logging config succeeded")
        except Exception as e:
            # sometimes we may met issue that the imported modules called
            # logging before logging init
            # remove root handler can workaround it
            logging.root.handlers = []
            logging.basicConfig(
                format="%(asctime)s %(levelname)s %(message)s", filename=constants.OPSMGRLOG,
                level=logging.INFO)
            logging.exception(e)
            logging.exception(
                "init_cli_logging :: exception when load logging configuration")
