# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.utils.translation import ugettext_lazy as _

from horizon import messages
from horizon import tabs

import logging

from openstack_dashboard.dashboards.operational_mgmt.inventory import tables
from openstack_dashboard.dashboards.operational_mgmt import rack
from openstack_dashboard.dashboards.operational_mgmt import resource

import opsmgr.inventory.device_mgr as device_mgr


class RackField(object):
    # The class "constructor" - It's actually an initializer
    def __init__(self, row_id, detail_title, detail_value):
        self.id = row_id
        self.detail_title = detail_title
        self.detail_value = detail_value


def make_rack_field(row_id, detail_title, detail_value):
    return RackField(row_id, detail_title, detail_value)


def retrieve_rack_resources(self):
    # retrieve resources for the rack id passed in (rack_id may be -1 on
    # initial pass)
    devices = []
    (rc, result_dict) = device_mgr.list_devices(None, False, None, None,
                                                False, False, [self.rack_id])
    if rc != 0:
        messages.error(self.request, _('Unable to retrieve Operational'
                                       ' Management inventory information'
                                       ' for resources.'))
        logging.error('Unable to retrieve Operational Management inventory'
                      ' information. A Non-0 return code returned from'
                      ' device_mgr.list_devices.  The return code is: %s', rc)
    else:
        all_devices = result_dict['devices']
        for raw_device in all_devices:
            devices.append(resource.Resource(raw_device))
    return devices


def retrieve_rack_metadata(self):
    # retrieve the rack details for the rack passed in (rack_id may be -1 on
    # initial pass)
    rack_meta_data = []
    (rc, result_dict) = device_mgr.list_racks(None, False, [self.rack_id])
    if rc != 0:
        messages.error(self.request, _('Unable to retrieve Operational'
                                       ' Management inventory information'
                                       ' for racks.'))
        logging.error('Unable to retrieve Operational Management inventory'
                      ' information. A Non-0 return code returned from'
                      ' device_mgr.list_racks.  The return code is: %s', rc)
    else:
        # We should have at least one resource in the results...just return
        # the metadata for the first value
        if len(result_dict['racks']) > 0:
            the_rack = rack.Rack(result_dict['racks'][0])
            counter = 0
            rack_meta_data.append(make_rack_field(counter, "Label",
                                                  the_rack.name))
            counter += 1
            rack_meta_data.append(make_rack_field(counter, "Data Center",
                                                  the_rack.data_center))
            counter += 1
            rack_meta_data.append(make_rack_field(counter, "Location",
                                                  the_rack.rack_loc))
            counter += 1
            rack_meta_data.append(make_rack_field(counter, "Notes",
                                                  the_rack.notes))
    return rack_meta_data


class RackTabBase(tabs.TableTab):
    table_classes = (tables.RackDetailsTable, tables.ResourcesTable,)
    template_name = ("op_mgmt/inventory/rack_tab.html")
    preload = False
    _has_more = False
    rack_fields = []
    rack_id = -1

    def get_resources_data(self):
        # Store the rack_id of the current rack into each action that
        # needs it
        tables.AddResourceLink.rack_id = self.rack_id
        tables.EditRackLink.rack_id = self.rack_id
        tables.RemoveRackLink.rack_id = self.rack_id
        # Return the list of resources
        return retrieve_rack_resources(self)

    def get_rack_details_data(self):
        return retrieve_rack_metadata(self)


class GenericTab(RackTabBase):
    name = _("GenericTab")
    slug = "generic_tab"

    def initialize(self, name, rack_id):
        self.name = name
        self.slug = name + "_tab"
        self.rack_id = rack_id


class DefaultTab(RackTabBase):
    name = _("Default")
    slug = "default_tab"
    rack_id = -1


class InventoryRacksTabs(tabs.TabGroup):
    slug = "inventoryRacks_tabs"
    # The tab group class requires at least one actual tab class to be
    # listed -- but we do not know how many tabs might be needed.  We'll
    # add a generic 'default' tab so that we can get created -- and then
    # add actual tabs in our init method
    tabs = (DefaultTab,)
    show_single_tab = True
    sticky = True

    def __init__(self, *args, **kwargs):
        # This will instantiate the default tab (needed so generic tabs can
        # be created for each rack)
        super(InventoryRacksTabs, self).__init__(*args, **kwargs)

        # to create each generic tab, the tab group and request are needed
        tab_group = self
        request = self._tabs['default_tab'].request

        # objects to hold new list of tabs (classes) and defined_tabs objects
        list_tabs = []   # hold list of new tab classes for the tab group
        defined_tabs = self._tabs.__class__()

        # Retrieve all defined racks (so the list of actual tabs can be
        # created)
        (rc, result_dict) = device_mgr.list_racks()
        if rc != 0:
            messages.error(self.request, _('Unable to retrieve Operational'
                                           ' Management inventory information'
                                           ' for racks.'))
            logging.error('Unable to retrieve Operational Management'
                          ' inventory information. A Non-0 return code'
                          ' returned from device_mgr.list_racks.  The'
                          ' return code is: %s', rc)
            return

        all_racks = result_dict['racks']

        # loop through each rack (creating a defined tab for each)
        for a_rack in all_racks:
            # For each rack, build a defined rack tab
            # create a defined rack tab (instantiating a generic tab)
            defined_rack_tab = GenericTab(tab_group, request)

            # initialize the defined rack tab (with rack information)
            defined_rack_tab.initialize(a_rack["label"], a_rack['rackid'])

            # Add the defineRackTab class to the list of classes in the
            # tab group
            list_tabs.append(defined_rack_tab.__class__)

            # Add the defineRackTab (the new tab) to the list of defined tabs
            defined_tabs[a_rack["label"] + "_tab"] = defined_rack_tab

        #  end loop through each rack

        # clear out that default tab from the tab group
        self._tabs.clear()
        # update the tab group with the list of defined tabs
        self._tabs.update(defined_tabs)
        # update tabs with the list of tab classes
        self.tabs = tuple(list_tabs)
