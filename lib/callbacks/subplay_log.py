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

class CallbackModule(object):

    def runner_on_ok(self, host, res):
        if 'var' in res:
            if 'play_output.results' in res['var']:
                for item in res['var']['play_output.results']:
                    if 'stdout_lines' in item:
                        print "\n".join(item['stdout_lines'])

    def v2_runner_on_ok(self, result):
        host = result._host.get_name()
        self.runner_on_ok(host, result._result)

