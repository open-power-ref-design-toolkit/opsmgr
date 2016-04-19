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
from django.utils.translation import ungettext_lazy
from horizon import tables
from horizon import forms
from horizon import messages
import opsmgr.inventory.device_mgr as device_mgr

import logging
import pdb

class AddResourceLink(tables.LinkAction):
    name = "addResource"
    verbose_name = _("Add Resource")
    url = "horizon:op_mgmt:inventory:addResource"
    classes = ("ajax-modal",)
    icon = "plus"
    rack_id = ""

    # dev: try this for multi-rack support
    def initialize(self, rack_id):
       self.rack_id = rack_id

class EditResourceLink(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Resource")
    url = "horizon:op_mgmt:inventory:editResource"
    classes = ("ajax-modal",)
    icon = "pencil"

class DeleteResourcesAction(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Resource",
            u"Delete Resource",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Resource",
            u"Deleted Resource",	
            count
        )

    def delete(self, request, obj_id):
        deviceIds = []
        deviceIds.append(obj_id)
   
        (rc, result_dict) = device_mgr.remove_device(None, False, deviceIds);
        
        if rc!=0:
           msg = _('Attempt to remove resource was not successful. Details of the attempt: "%s"' % result_dict)
           messages.error(request, msg)
        else:
           # Default message displays the device ID instead of the device label...do we need to use our own message here?  How?
           #msg = _('Attempt to remove resources was successful.')
           #messages.info(request, msg)

           return  # allow the base class to display the success message

class EditRack(tables.LinkAction):
    name = "editRack"
    verbose_name = _("Edit Rack")
    url = "horizon:op_mgmt:inventory:edit_rack"
    classes = ("ajax-modal",)
    icon = "pencil"
    def __init__(self, attrs=None, **kwargs):
        super(EditRack, self).__init__(attrs, **kwargs)

class RemoveRackAction(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Remove",
            u"Remove",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Removed Rack",
            u"Removed Rack",
            count
        )

    # TODO:  Not getting called -- so we're not able to delete anything
    def delete(self, request, obj_id):
        logging.error(" in the delete method!")
        #pdb.set_trace()
        #api.nova.aggregate_delete(request, obj_id)

class ResourceFilterAction(tables.FilterAction):
    def filter(self, table, devices, filter_string):
        #pdb.set_trace()
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [resource for resource in resources
                if q in resource.label.lower()]

def get_link_value(device):
    if not hasattr(device, 'web_url') or device.web_url is None:
        return _("")
    else:
        return device.web_url

def get_link_target(device):
    return _(device.label)
class ResourcesTable(tables.DataTable):
    # TODO:  The reference to link target isn't working because the value of it is being set
    # to the method call get_link_target(xx) instead of the value returned from that
    # method....
    label = tables.Column('label',
                          form_field=forms.CharField(),
                          verbose_name=_("Label"),
                          link=get_link_value,
                          link_attrs={'target': get_link_target})
    type = tables.Column('type', \
                        verbose_name=_("Type"))
    rackLoc = tables.Column('rackLoc', \
                                verbose_name=_("EIA Location"))
    userid = tables.Column('userid', \
                          verbose_name=_("Management User"))
    mtm = tables.Column('mtm', \
                       verbose_name=_("Machine Type/Model"))
    sn = tables.Column('sn', \
                      verbose_name=_("Serial Number"))
    mgmtIpaV4 = tables.Column('mgmtIpaV4', \
                      verbose_name=_("IP Address"))
    version = tables.Column('version', \
                      verbose_name=_("Installed Version"))
    deviceId = tables.Column('deviceId', \
                      hidden = True,
                      verbose_name = _("Device ID"))
    class Meta(object):
        name = "resources"
        verbose_name = _("Resources")
        rack_id = ""
        row_actions = (EditResourceLink, DeleteResourcesAction)
        table_actions = (ResourceFilterAction, AddResourceLink, DeleteResourcesAction)

class RackDetailsTable(tables.DataTable):  
    detailTitle = tables.Column('detailTitle',
                          attrs={'width': '150px',},
                          verbose_name=_("Rack Property"))
    detailvValue = tables.Column('detailValue', \
                        attrs={'width': '400px',},
                        verbose_name=_("Value"))
    rackId = tables.Column('rackId', \
                      hidden = True,
                      verbose_name = _("Rack ID"))
    class Meta(object):
          name = "rack_details"
          verbose_name = _("Rack Details")
          multi_select = False
          footer=False
          filter = False
          table_actions = (EditRack, RemoveRackAction)
