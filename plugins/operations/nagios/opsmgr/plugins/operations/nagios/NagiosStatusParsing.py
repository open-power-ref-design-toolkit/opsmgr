# Copyright 2017, IBM US, Inc.
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

import re

StatusTypes = ["OK", "WARNING", "CRITICAL", "UNKNOWN", "OK:"]


def parse_host_data(data_lines):
    # parse host data in .dat file
    # look for keywords only (hoststatus) in data and save to stats{}
    stats = {}
    host_num = 0
    line_cnt = 0
    for line in data_lines:
        if (line == "hoststatus {"):
            # get host_name (next line), Ex. host_name=cephosd-23
            next_line = data_lines[line_cnt + 1]
            host_name = next_line.split('host_name=')[1]

            # search for plugin_output line & save data
            # Ex. plugin_output=PING OK - Packet loss = 0%, RTA = 0.51 ms
            j = line_cnt
            for status_line in data_lines:
                next_line = data_lines[j]
                host_status_type = next_line.split('=')[0]

                if (host_status_type == "plugin_output"):
                    # read status string after '=' and find the status
                    host_status_str = next_line.split('=')[1]
                    host_status, rc = _parse_status(host_status_str)
                    if rc == 0:
                        # don't need to save non-error string
                        if (host_status == "OK"):
                            host_status_str = ""
                        else:
                            host_status_str = host_status_str.split('- ')[1]
                        # read line into array
                        stats[host_num] = {'host_name': host_name, 'host_status': host_status, 'host_err': host_status_str}
                        host_num += 1
                        break
                j += 1
        line_cnt += 1

    return stats


def parse_service_data(data_lines):
    # parse service data in .dat file
    # look for keywords only (servicestatus) and save to stats[]
    stats = {}
    service_num = 0
    line_cnt = 0

    for line in data_lines:
        if (line == "servicestatus {"):
            # get host_name (next line down)
            # Ex. host_name=cephosd-23
            next_line = data_lines[line_cnt + 1]
            host_name = next_line.split('host_name=')[1]

            # get service_name (next line down after host)
            # Ex. service_description=Ceph OSD Server
            next_line = data_lines[line_cnt + 2]
            service_name = next_line.split('service_description=')[1]

            # search for plugin_output line & save string
            # Ex. plugin_output=SSH OK - OpenSSH_7.2p2 Ubuntu-4ubuntu2.1 (protocol 2.0)
            # Ex. plugin_output=OK - 1 plugins checked, 1 ok
            j = line_cnt + 2
            for status_line in data_lines:
                next_line = data_lines[j]
                service_status_type = next_line.split('=')[0]

                # Ex, plugin_output=CRITICAL - 12 plugins checked, 1 critical (server-disk),
                #                              11 ok [please don't run plugins as root!]
                if (service_status_type == "plugin_output"):
                    # read status string after the '=' and get the status
                    service_status_str = next_line.split('=')[1]
                    service_status, rc = _parse_status(service_status_str)

                    # need to search string for service_status and then save rest of string
                    # Ex. UNKNOWN - 2 plugins checked, 2 unknown (osa_compute_nova, osa_compute_libvirt)
                    if (rc == 0 and service_status == "UNKNOWN"):
                        unknown_str = "unknown"
                        pattern = '(.*\,) (.*) (' + unknown_str + ') (\(.*\))'
                        match_status = re.search(pattern, service_status_str)
                        if match_status:
                            # get all the unknown types from plugin_output
                            unknown_num_str = match_status.group(2)
                            unknown_service_type = _get_unknown_types(match_status)
                            if unknown_service_type:
                                # read next line which is long_plugin_output
                                next_line = data_lines[j + 1]
                                service_status_type, long_plugin_str = next_line.split('=', 1)

                                # search for the unknown strings
                                num = 0
                                loop_cnt = 0
                                while (num < int(unknown_num_str)):
                                    # set the search pattern
                                    pattern = '(\[.*\]) (.*' + unknown_service_type[num] + '.*)'
                                    plugin_info_strings = long_plugin_str.split('\\n')[loop_cnt]
                                    loop_cnt += 1

                                    # skip over empty lines
                                    if (len(plugin_info_strings) > 1):
                                        # remove the [] and search for unknown type
                                        service_error_str = re.search(pattern, plugin_info_strings)

                                        # check for match first
                                        if service_error_str:
                                            # remove unknown type from beginning of string and remove []
                                            service_error = service_error_str.group(2).split('[')[1].strip(']')
                                            stats[service_num] = {'host_name': host_name, 'service_name': service_name,
                                                                  'service_status': service_status,
                                                                  'service_err': service_error}
                                            service_num += 1
                                            num += 1

                    # check if WARNING/CRITICAL in order to capture message in long_plugin_output
                    # Ex. long_plugin_output= ...[ 2] server-mem MEM OK - free system memory: 268 MB\n
                    #                            [ 3] server-disk CheckDisk CRITICAL: / 96%\n ...
                    elif (rc == 0 and service_status != "OK"):
                        # determine the number of plugins checked for errors
                        plugin_str = service_status_str.split('- ')[1]
                        plugin_num_str = plugin_str.split(' ')[0]

                        # read next line which is long_plugin_output
                        next_line = data_lines[j + 1]
                        service_status_type, long_plugin_str = next_line.split('=', 1)
                        if (service_status_type == "long_plugin_output"):
                            # check for empty string, which is the case for localhost
                            if len(long_plugin_str) < 1:
                                stats[service_num] = {'host_name': host_name, 'service_name': service_name,
                                                      'service_status': service_status, 'service_err': service_status_str}
                                service_num += 1
                            else:
                                # set the search pattern
                                pattern = '(\[.*\]) (.*' + service_status + '.*)'
                                num = 0
                                loop_cnt = 0
                                while (num < int(plugin_num_str)):
                                    plugin_info_strings = long_plugin_str.split('\\n')[loop_cnt]
                                    loop_cnt += 1
                                    # remove the [] and search for CRITICAL/WARNING
                                    # skip over empty lines
                                    if (len(plugin_info_strings) > 1):
                                        service_error_str = re.search(pattern, plugin_info_strings)
                                        if service_error_str:
                                            if (service_error_str.group(2).split('[')):
                                                service_err_str = service_error_str.group(2).split('[')[0]
                                            else:
                                                service_err_str = service_error_str.group(2)
                                            stats[service_num] = {'host_name': host_name, 'service_name': service_name,
                                                                  'service_status': service_status,
                                                                  'service_err': service_err_str}
                                            service_num += 1
                                        num += 1
                    # OK status or not readable status, so don't need to store error status
                    else:
                        stats[service_num] = {'host_name': host_name, 'service_name': service_name,
                                              'service_status': service_status, 'service_err': ""}
                        service_num += 1
                    break
                j += 1
        line_cnt += 1

    return stats


def _parse_status(service_status_str):
    # search string for valid status type
    service_status = ""

    for num in range(len(StatusTypes)):
        pattern = '(.*' + StatusTypes[num] + ') (.*)'
        match_status = re.search(pattern, service_status_str)
        if match_status:
            break

    if match_status:
        service_status = StatusTypes[num]
        if service_status == "OK:":
            service_status = "OK"
        service_status_str = match_status.group(2)
        rc = 0
    else:
        rc = 1

    return service_status, rc


def _get_unknown_types(match_status):
    unknown_service_type = {}
    unknown_num_str = match_status.group(2)

    # need to remove () from group
    unknown_err_types = match_status.group(4).strip('()')
    if unknown_err_types:
        for num in range(int(unknown_num_str)):
            if (int(unknown_num_str) > 1):
                # split string & remove leading space
                unknown_service_type[num] = unknown_err_types.split(', ')[num]
            else:
                unknown_service_type[num] = unknown_err_types
    return (unknown_service_type)
