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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from openstack_dashboard import api
#from openstack_dashboard import policy

import logging
import pdb

from openstack_dashboard.dashboards.operational_mgmt.inventory \
    import forms as project_forms
from openstack_dashboard.dashboards.operational_mgmt.inventory \
    import tables as project_tables
from openstack_dashboard.dashboards.operational_mgmt.inventory \
    import tabs as inventoryRacks_tabs
import opsmgr.inventory.device_mgr as device_mgr
import gc

class IndexView(tabs.TabbedTableView):
    tab_group_class = inventoryRacks_tabs.InventoryRacksTabs    
    table_class = project_tables.ResourcesTable
    template_name = 'op_mgmt/inventory/index.html'

class EditResourceView(forms.ModalFormView):
    template_name = 'op_mgmt/inventory/editResource.html'
    modal_header = _("Edit Resource")
    form_id = "edit_resource_form"
    form_class = project_forms.EditResourceForm
    submit_label = _("Edit Resource")
    submit_url = "horizon:op_mgmt:inventory:editResource"
    success_url = reverse_lazy('horizon:op_mgmt:inventory:index')
    page_title = _("Edit Resource")

    @memoized.memoized_method
    def get_object(self):
        try:
            (rc, result_dict) = device_mgr.list_devices(None, False, None, [self.kwargs['resource_id']])
            if rc!=0:
               messages.error(self.request, _('Unable to retrive resource to be edited.'))
               return
            else:
               value = result_dict['devices']
               # loop through each raw device
               for raw_device in value:
                  # should only be 1 -- return the first found
                  return raw_device
        except Exception:
            redirect = reverse("horizon:op_mgmt:inventory:index")
            exceptions.handle(self.request,
                              _('Unable to retrive resource to be edited.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(EditResourceView, self).get_context_data(**kwargs)
        args = (self.get_object()['deviceid'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        raw_device = self.get_object()
        return {'label': raw_device['label'],
                              'rackid': raw_device['rackid'],
                              'eiaLocation': raw_device['rack-eia-location'],
                              'ip_address': raw_device['ip-address'],
                              'userID': raw_device['userid'],
                              'deviceId': raw_device['deviceid']}

class AddResourceView(forms.ModalFormView):
    template_name = 'op_mgmt/inventory/addResource.html'
    modal_header = _("Add Resource")
    form_id = "add_resource_form"
    form_class = project_forms.AddResourceForm
    submit_label = _("Add Resource")
    submit_url = reverse_lazy("horizon:op_mgmt:inventory:addResource")
    success_url = reverse_lazy('horizon:op_mgmt:inventory:index')
    page_title = _("Add Resource")

    def get_initial(self):
       return {'rackid': ""}

class EditRackView(forms.ModalFormView):
    form_class = project_forms.EditRack
    form_id = "edit_rack"
    template_name = 'op_mgmt/inventory/edit_rack.html'
    success_url = reverse_lazy("horizon:op_mgmt:inventory:index")
    context_object_name = 'id'
    modal_id = "edit_rack_modal"
    modal_header = _("Edit Rack Details")
    submit_label = _("Save Changes")
    submit_url = reverse_lazy("horizon:op_mgmt:inventory:edit_rack")
    
    def get_initial(self):
        self.rack = self.get_object()        
        initial = super(EditRackView, self).get_initial()
        if self.rack:
           return {'label': self.rack['label'],
                              'data_center': self.rack['data_center'],
                              'location': self.rack['location'],
                              'notes': self.rack['notes']}
        else:
           return
    def get_context_data(self, **kwargs):
        context = super(EditRackView, self).get_context_data(**kwargs)
        if self.get_form():
           context['form'] = self.get_form()
        device = self.get_object()
        if "label" in self.kwargs:
           args = (self.kwargs['label'],)
        
        if "label" in self.kwargs:
           context['id'] = self.kwargs['label']
        return context
    @memoized.memoized_method
    def get_form(self, **kwargs):
        form_class = kwargs.get('form_class', self.get_form_class())
        return super(EditRackView, self).get_form(form_class)
    def get_object(self):
        if "label" in self.kwargs:
           (rc, result_dict) = device_mgr.list_racks(None, False, [self.kwargs["label"]])
        else:
           # we were called with no context of what to edit...just return
           return

        if rc!=0:
           messages.error(self.request, _('Unable to retrive rack to be edited.'))
        else:
           value = result_dict['racks']
           # loop through each raw device
           for rack in value:
              # should only be 1
              return rack
