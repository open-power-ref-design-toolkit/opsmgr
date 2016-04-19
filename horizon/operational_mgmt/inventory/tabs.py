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

from horizon import tabs
from horizon import messages
import logging
import pdb

from openstack_dashboard.dashboards.operational_mgmt.inventory import tables
from openstack_dashboard.dashboards.operational_mgmt import resource
import opsmgr.inventory.device_mgr as device_mgr


class Rack_Field(object):
    # The class "constructor" - It's actually an initializer 
    def __init__(self, id, detailTitle, detailValue, rackid):
        self.id = id
        self.detailTitle= detailTitle
        self.detailValue = detailValue
        self.rackid = rackid
def make_rack_field(id, detailTitle, detailValue, rackid):
    return Rack_Field(id, detailTitle, detailValue, rackid)

def retrieve_rack_resources(rack_id):
    # retrieve resources for the rack id passed in (rack_id may be -1 on initial pass)
    devices = [] 
    (rc, result_dict) = device_mgr.list_devices(None, False, None, None, False, False, [rack_id])
    if rc!=0:
      messages.error(self.request, _('Unable to retrieve Operational Management inventory information for resources.'))
      logging.error('Unable to retrieve Operational Management inventory information.  '
                    'A Non-0 return code returned from device_mgr.list_devices.  The return code is: %s' % rc)  
    else:
       value = result_dict['devices']       
       for raw_device in value:
          devices.append(resource.Resource(raw_device))
    return devices

class RackTabBase(tabs.TableTab):
    table_classes = (tables.RackDetailsTable, tables.ResourcesTable,)
    template_name = ("op_mgmt/inventory/rack_tab.html")
    preload = False
    _has_more = False
    rack_fields = []
    
    def get_resources_data(self):
       # dev:  attempt to store the rack_id of the current rack in the add resource link (for priming purposes)
       tables.AddResourceLink.rack_id = self.rack_id
       
       return retrieve_rack_resources(self.rack_id)

    def get_rack_details_data(self):
       return self.rack_fields
    def set_rack_metadata(self, metadata):
       self.rack_fields = metadata

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
    # TODO:  For whatever reason, when you have multiple tabs, the table breaks down (the table is no longer
    # passed along (so we loose the ability to delete for all tabs *except* for the last tab added))

    slug = "inventoryRacks_tabs"
    # The tab group class requires at least one actual tab class to be listed -- but we do not know how many
    # tabs might be needed.  We'll add a generic 'default' tab so that we can get created --
    # and then add actual tabs in our init method
    tabs = (DefaultTab, )  
    show_single_tab = True
    sticky = True

    def __init__(self, *args, **kwargs):
        # We must first try to retrieve all racks
        (rc2, result_dict) = device_mgr.list_racks() 

        if rc2!=0:
           messages.error(self.request, _('Unable to retrieve Operational Management inventory information for rack extensions.'))
           logging.error('Unable to retrieve Operational Management rack inventory information.'
                         'A Non-0 return code returned from device_mgr.list_racks.  The return code is: %s' % rc)    
        # This will instantiate our default tab (needed so we can create our generic tabs) 
        super(InventoryRacksTabs, self).__init__(*args, **kwargs)        
        self.load_tab_data()  # should only be the default tab (and it should have no elements)

        # objects to hold the new list of tabs (classes) and definedTabs objects
        listTabs = []      
        definedTabs = self._tabs.__class__()

   
        # needed to instantiate each defined tab
        tab_group = self._tabs['default_tab'].tab_group  
        request = self._tabs['default_tab'].request

        value = result_dict['racks']
        # loop through each rack
        for s in value:
           # For each rack, build a defined rack tab    
           #pdb.set_trace()
           deviceLabel = s["label"]
           deviceRackId = s['rackid']
           definedRackTab = GenericTab(tab_group, request)
           definedRackTab.initialize(deviceLabel, deviceRackId)

           # build our rack metadata object
           rackMetaData = []
           counter = 0
           rackMetaData.append(make_rack_field(counter, "Label", deviceLabel, deviceRackId))
           counter += 1
           rackMetaData.append(make_rack_field(counter, "Data Center", s['data-center'], deviceRackId))
           counter += 1
           rackMetaData.append(make_rack_field(counter, "Location", s['location'], deviceRackId))
           counter += 1
           rackMetaData.append(make_rack_field(counter, "Notes", s['notes'], deviceRackId))
           counter += 1
           definedRackTab.set_rack_metadata(rackMetaData)
           listTabs.append(definedRackTab.__class__)

           # Add our new tab to the list of defined tabs                
           definedTabs[deviceLabel +"_tab"] = definedRackTab

        # clear out the default tab from the tab group
        self._tabs.clear()
        # update the tab group with the list of defined tabs
        self._tabs.update(definedTabs)
        # update tabs with the list of tab classes
        self.tabs = tuple(listTabs)
