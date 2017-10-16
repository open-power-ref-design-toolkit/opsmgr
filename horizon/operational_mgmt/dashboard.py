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

from django.utils.translation import ugettext_lazy as _

import horizon
import imp
import os
import sys


def get_module_path(module_name):
    """Gets the module path without importing anything.

    Avoids conflicts with package dependencies.
    (taken from http://github.com/sitkatech/pypatch)
    """
    path = sys.path
    for name in module_name.split('.'):
        file_pointer, path, desc = imp.find_module(name, path)
        path = [path, ]
        if file_pointer is not None:
            file_pointer.close()

    return os.path.dirname(path[0])


def find_settings_file():
    module_path = os.path.abspath(
        get_module_path(os.environ['DJANGO_SETTINGS_MODULE'])
    )
    settings_dir = os.path.join(module_path, 'local')
    settings_file = os.path.join(settings_dir, 'local_settings.py')
    return settings_file


def minimal_footprint():
    settingsFile = file(find_settings_file())
    found = False
    for line in settingsFile:
        if "patch_ui = True" in line:
            found = True
            break
    return found


class OpMgmtdashboard(horizon.Dashboard):
    name = _("Operational Management")
    slug = "op_mgmt"
    panels = ("inventory",)  # ,"monitoring","logging")
    default_panel = 'inventory'

horizon.register(OpMgmtdashboard)
# When in minimal-footprint (standard) environment, hide the other
# dashboards.
if (minimal_footprint()):
    # Hide project dashboard
    try:
        project = horizon.get_dashboard('project')
        project.permissions = ('openstack.roles.hideMe')
    except:
        # consider logging that we're not able to hide other dashboards
        pass
    # Hide admin dashboard
    try:
        project = horizon.get_dashboard('admin')
        project.permissions = ('openstack.roles.hideMe')
    except:
        # consider logging that we're not able to hide other dashboards
        pass
    # Hide identity dashboard
    try:
        project = horizon.get_dashboard('identity')
        project.permissions = ('openstack.roles.hideMe')
    except:
        # consider logging that we're not able to hide other dashboards
        pass
