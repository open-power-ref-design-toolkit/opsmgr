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
from django.utils.decorators import method_decorator  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters  # noqa

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tabs
from horizon.utils import memoized

import logging

from openstack_dashboard.dashboards.operational_mgmt.inventory \
    import forms as project_forms
from openstack_dashboard.dashboards.operational_mgmt.inventory \
    import tables as project_tables
from openstack_dashboard.dashboards.operational_mgmt.inventory \
    import tabs as inventoryRacks_tabs
import opsmgr.inventory.device_mgr as device_mgr


class IndexView(tabs.TabbedTableView):
    tab_group_class = inventoryRacks_tabs.InventoryRacksTabs
    table_class = project_tables.ResourcesTable
    template_name = 'op_mgmt/inventory/index.html'


class AddResourceView(forms.ModalFormView):
    template_name = 'op_mgmt/inventory/addResource.html'
    modal_header = _("Add Resource")
    form_id = "add_resource_form"
    form_class = project_forms.AddResourceForm
    submit_label = _("Add Resource")
    submit_url = "horizon:op_mgmt:inventory:addResource"
    success_url = reverse_lazy('horizon:op_mgmt:inventory:index')
    page_title = _("Add Resource")

    def get_initial(self):
        # Need the rack for the active tab
        rack = self.get_object()
        # Prime the rack information on our AddResourceForm
        if rack:
            return {'rackid': rack['rackid'],
                    'rack_label': rack['label']}
        else:
            return

    @memoized.memoized_method
    def get_object(self):
        failure_message = str("Unable to retrieve rack information " +
                              " for the resource being added.")
        if "rack_id" in self.kwargs:
            try:
                (rc, result_dict) = device_mgr.list_racks(
                    None, False, [self.kwargs["rack_id"]])
            except Exception as e:
                logging.error("Exception received trying to retrieve rack"
                              " information.  Exception is: %s", e)
                exceptions.handle(self.request, failure_message)
                return
        else:
            # This is unexpected.  AddResourceView called with no context of
            # what rack the resource is being added.  Need to display an error
            # message because the dialog will not be primed with required data
            logging.error("AddResourceView called with no context.")
            messages.error(self.request, failure_message)
            return

        if rc != 0:
            messages.error(self.request, failure_message)
            return
        else:
            # We should have at least one rack in the results...just return
            # the first value
            if len(result_dict['racks']) > 0:
                return result_dict['racks'][0]
            else:
                messages.error(self.request, failure_message)
                return

    def get_context_data(self, **kwargs):
        # place the rack id onto the submit url
        context = super(AddResourceView, self).get_context_data(**kwargs)
        args = (self.get_object()['rackid'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context


class EditResourceView(forms.ModalFormView):
    template_name = 'op_mgmt/inventory/editResource.html'
    modal_header = _("Edit Resource")
    form_id = "edit_resource_form"
    form_class = project_forms.EditResourceForm
    submit_label = _("Edit Resource")
    submit_url = "horizon:op_mgmt:inventory:editResource"
    success_url = reverse_lazy('horizon:op_mgmt:inventory:index')
    page_title = _("Edit Resource")

    def get_initial(self):
        # Need the device being edited
        device = self.get_object()
        if device:
            return {'label': device['label'],
                    'auth_method': device['auth_method'],
                    'rackid': device['rackid'],
                    'eiaLocation': device['rack-eia-location'],
                    'ip_address': device['ip-address'],
                    'userID': device['userid'],
                    'deviceId': device['deviceid']}
        else:
            return

    @memoized.memoized_method
    def get_object(self):
        failure_message = str("Unable to retrieve resource information" +
                              " for the resource being edited.")
        if "resource_id" in self.kwargs:
            try:
                (rc, result_dict) = device_mgr.list_devices(
                    None, False, None, [self.kwargs['resource_id']])
            except Exception as e:
                logging.error("Exception received trying to retrieve"
                              " resource information.  Exception is: %s", e)
                exceptions.handle(self.request, failure_message)
                return
        else:
            # This is unexpected.  EditResourceView called with no context
            # of what to edit.  Need to display an error message because the
            # dialog will not be primed with required data
            logging.error("EditResourceView called with no context.")
            messages.error(self.request, failure_message)
            return

        if rc != 0:
            messages.error(self.request, failure_message)
            return
        else:
            # We should have at least one resource in the results...just
            # return the first value
            if len(result_dict['devices']) > 0:
                return result_dict['devices'][0]
            else:
                messages.error(self.request, failure_message)
                return

    def get_context_data(self, **kwargs):
        # place the device id on to the submit url
        context = super(EditResourceView, self).get_context_data(**kwargs)
        args = (self.get_object()['deviceid'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context


class ChangePasswordView(forms.ModalFormView):
    template_name = 'op_mgmt/inventory/changePassword.html'
    modal_header = _("Change Password")
    form_id = "change_password_form"
    form_class = project_forms.ChangePasswordForm
    submit_label = _("Change Password")
    submit_url = "horizon:op_mgmt:inventory:changePassword"
    success_url = reverse_lazy('horizon:op_mgmt:inventory:index')
    page_title = _("Change Password")

    @method_decorator(sensitive_post_parameters('password',
                                                'confirm_password'))
    def dispatch(self, *args, **kwargs):
        return super(ChangePasswordView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        # Need the device and user information to prime the dialog
        device = self.get_object()
        if device:
            return {'label': device['label'],
                    'userID': device['userid'],
                    'deviceid': device['deviceid']}
        else:
            return

    @memoized.memoized_method
    def get_object(self):
        failure_message = str("Unable to retrieve resource information for" +
                              " the resource being edited.")
        if "resource_id" in self.kwargs:
            try:
                (rc, result_dict) = device_mgr.list_devices(
                    None, False, None, [self.kwargs['resource_id']])
            except Exception as e:
                logging.error("Exception received trying to retrieve"
                              " resource information.  Exception is: %s", e)
                exceptions.handle(self.request, failure_message)
                return
        else:
            # This is unexpected.  ChangePasswordView called with no context
            # of what to edit.  Need to display an error message because the
            # dialog will not be primed with required data
            logging.error("ChangePasswordView called with no context.")
            messages.error(self.request, failure_message)
            return

        if rc != 0:
            messages.error(self.request, failure_message)
            return
        else:
            # We should have at least one resource in the results...just
            # return the first value
            if len(result_dict['devices']) > 0:
                return result_dict['devices'][0]
            else:
                messages.error(self.request, failure_message)
                return

    def get_context_data(self, **kwargs):
        # place the device id on the submit url
        context = super(ChangePasswordView, self).get_context_data(**kwargs)
        args = (self.get_object()['deviceid'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context


class EditRackView(forms.ModalFormView):
    template_name = 'op_mgmt/inventory/editRack.html'
    modal_header = _("Edit Rack Details")
    form_id = "edit_rack"
    form_class = project_forms.EditRackForm
    submit_label = _("Edit Rack")
    submit_url = "horizon:op_mgmt:inventory:editRack"
    success_url = reverse_lazy("horizon:op_mgmt:inventory:index")

    def get_initial(self):
        # Need the rack being edited
        rack = self.get_object()
        if rack:
            return {'rack_id': rack['rackid'],
                    'label': rack['label'],
                    'data_center': rack['data-center'],
                    'location': rack['location'],
                    'notes': rack['notes']}
        else:
            return

    @memoized.memoized_method
    def get_object(self):
        failure_message = str("Unable to retrieve rack information" +
                              " for the rack being edited.")
        if "rack_id" in self.kwargs:
            try:
                (rc, result_dict) = device_mgr.list_racks(
                    None, False, [self.kwargs["rack_id"]])
            except Exception as e:
                logging.error("Exception received trying to retrieve"
                              " rack information.  Exception is: %s", e)
                exceptions.handle(self.request, failure_message)
                return
        else:
            # This is unexpected.  EditRackView called with no context
            # of what to edit.  Need to display an error message because
            # the dialog will not be primed with required data
            logging.error("EditRackView called with no context.")
            messages.error(self.request, failure_message)
            return

        if rc != 0:
            messages.error(self.request, failure_message)
            return
        else:
            # We should have at least one resource in the results...just
            # return the first value
            if len(result_dict['racks']) > 0:
                return result_dict['racks'][0]
            else:
                messages.error(self.request, failure_message)
                return

    def get_context_data(self, **kwargs):
        # place the device id on to the submit url
        context = super(EditRackView, self).get_context_data(**kwargs)
        args = (self.get_object()['rackid'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context


class RemoveRackView(forms.ModalFormView):
    template_name = 'op_mgmt/inventory/removeRack.html'
    modal_header = _("Confirm Remove Rack")
    form_id = "remove_rack_form"
    form_class = project_forms.RemoveRackForm
    submit_label = _("Remove Rack")
    submit_url = "horizon:op_mgmt:inventory:removeRack"
    success_url = reverse_lazy("horizon:op_mgmt:inventory:index")
    page_title = _("Confirm Remove Rack")

    def get_initial(self):
        # Need the rack being edited
        rack = self.get_object()
        if rack:
            return {'rack_id': rack['rackid'],
                    'label': rack['label']}
        else:
            return

    @memoized.memoized_method
    def get_object(self):
        failure_message = str("Unable to retrieve rack information" +
                              " for the rack being removed.")
        if "rack_id" in self.kwargs:
            try:
                (rc, result_dict) = device_mgr.list_racks(
                    None, False, [self.kwargs["rack_id"]])
            except Exception as e:
                logging.error("Exception received trying to retrieve"
                              " rack information.  Exception is: %s", e)
                exceptions.handle(self.request, failure_message)
                return
        else:
            # This is unexpected.  RemoveRackView called with no context
            # of what to edit.  Need to display an error message because
            # the dialog will not be primed with required data
            logging.error("RemoveRackView called with no context.")
            messages.error(self.request, failure_message)
            return

        if rc != 0:
            messages.error(self.request, failure_message)
            return
        else:
            # We should have at least one resource in the results...just
            # return the first value
            if len(result_dict['racks']) > 0:
                return result_dict['racks'][0]
            else:
                messages.error(self.request, failure_message)
                return

    def get_context_data(self, **kwargs):
        # place the device id on to the submit url
        context = super(RemoveRackView, self).get_context_data(**kwargs)
        args = (self.get_object()['rackid'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context


class RemoveResourceView(forms.ModalFormView):
    template_name = 'op_mgmt/inventory/removeResource.html'
    modal_header = _("Remove Resource")
    form_id = "remove_resource_form"
    form_class = project_forms.RemoveResourceForm
    submit_label = _("Remove Resource")
    submit_url = "horizon:op_mgmt:inventory:removeResource"
    success_url = reverse_lazy('horizon:op_mgmt:inventory:index')
    page_title = _("Remove Resource")

    def get_initial(self):
        # Need the device being edited
        device = self.get_object()
        if device:
            return {'label': device['label'],
                    'deviceId': device['deviceid']}
        else:
            return

    @memoized.memoized_method
    def get_object(self):
        failure_message = str("Unable to retrieve resource information" +
                              " for the resource being removed.")
        if "resource_id" in self.kwargs:
            try:
                (rc, result_dict) = device_mgr.list_devices(
                    None, False, None, [self.kwargs['resource_id']])
            except Exception as e:
                logging.error("Exception received trying to retrieve"
                              " resource information.  Exception is: %s", e)
                exceptions.handle(self.request, failure_message)
                return
        else:
            # This is unexpected.  RemoveResourceView called with no context
            # of what to edit.  Need to display an error message because the
            # dialog will not be primed with required data
            logging.error("RemoveResourceView called with no context.")
            messages.error(self.request, failure_message)
            return

        if rc != 0:
            messages.error(self.request, failure_message)
            return
        else:
            # We should have at least one resource in the results...just
            # return the first value
            if len(result_dict['devices']) > 0:
                return result_dict['devices'][0]
            else:
                messages.error(self.request, failure_message)
                return

    def get_context_data(self, **kwargs):
        # place the device id on to the submit url
        context = super(RemoveResourceView, self).get_context_data(**kwargs)
        args = (self.get_object()['deviceid'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context
