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

from django.core.urlresolvers import reverse
from django import shortcuts
from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import messages
from horizon import tables

import opsmgr.inventory.resource_mgr as resource_mgr

import logging


class AddResourceLink(tables.LinkAction):
    name = "addResource"
    verbose_name = _("Add Resource")
    url = "horizon:op_mgmt:inventory:addResource"
    classes = ("ajax-modal",)
    icon = "plus"
    rack_id = ""

    # required to prime the add resource dialog with the rack id
    def get_link_url(self):
        if self.rack_id != "":
            return reverse(self.url, args=[self.rack_id])
        else:
            return self.url


class RemoveResources(tables.Action):
    name = "removeResources"
    verbose_name = "Remove Resource"
    classes = ('btn-danger', 'btn-detach')
    help_text = _("This action cannot be undone.")

    def get_default_attrs(self):
        """Returns a list of the default HTML attributes for the action."""
        attrs = super(RemoveResources, self).get_default_attrs()
        # This action must behave like a batch-action activity with
        # regards to enablement/disablement...
        attrs.update({'data-batch-action': 'true'})
        return attrs

    def get_success_url(self, request):
        return reverse('horizon:op_mgmt:inventory:index')

    def handle(self, data_table, request, object_ids):
        __method__ = 'tables.RemoveResources.handle'
        logging.debug("%s: Attempt to remove resources %s ",
                      __method__, object_ids)

        if len(object_ids) <= 0:
            return shortcuts.redirect(self.get_success_url(request))

        try:
            (rc, result_dict) = resource_mgr.remove_resource(None, False,
                                                             object_ids)
            if rc != 0:
                # Log details of the unsuccessful attempt.
                logging.error("%s: Attempt to remove resources "
                              "failed.", __method__)
                logging.error(
                    "%s: Unable to remove resources. A Non-0 "
                    " return code returned from resource_mgr.remove_resource."
                    " The return code is: %s. Details of the attempt: "
                    " %s", __method__, rc, result_dict)
                # Show generic failure message
                msg = str(
                    'Attempt to remove resources was not successful.  ' +
                    'Details of the attempt: ' + result_dict)
                messages.error(request, msg)
            else:
                # Show generic success message
                msg = str('Resources successfully removed.')
                messages.success(request, msg)
        except Exception as e:
            redirect = reverse('horizon:op_mgmt:inventory:index')
            logging.error("%s: Exception received trying to remove  "
                          "resources with ids %s.  Exception is: %s",
                          __method__, object_ids, e)
            exceptions.handle(request, _('Unable to remove resources.'),
                              redirect=redirect)

        return shortcuts.redirect(self.get_success_url(request))


class EditResourceLink(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Resource")
    url = "horizon:op_mgmt:inventory:editResource"
    classes = ("ajax-modal",)
    icon = "pencil"


class ChangePasswordLink(tables.LinkAction):
    name = "changePassword"
    verbose_name = _("Change Password")
    url = "horizon:op_mgmt:inventory:changePassword"
    classes = ("ajax-modal",)
    icon = "pencil"


# Link opens default remove/delete dialog to individual resources
# from a rack definition
class RemoveResourceLink(tables.LinkAction):
    name = "removeResource"
    verbose_name = _("Remove Resource")
    url = "horizon:op_mgmt:inventory:removeResource"
    # consider adding class to indicate action is 'dangerous' --
    # btn-danger makes the words black, and background red: a bit much
    classes = ("ajax-modal",)
    icon = "trash"


class EditRackLink(tables.LinkAction):
    name = "editRack"
    verbose_name = _("Edit Rack")
    url = "horizon:op_mgmt:inventory:editRack"
    classes = ("ajax-modal",)
    icon = "pencil"
    rack_id = ""

    # required to prime the edit rack dialog with the rack id
    def get_link_url(self):
        if self.rack_id != "":
            return reverse(self.url, args=[self.rack_id])
        else:
            return self.url


class RemoveRackLink(tables.LinkAction):
    name = "removeRack"
    verbose_name = _("Remove Rack")
    url = "horizon:op_mgmt:inventory:removeRack"
    classes = ("ajax-modal", "btn-danger",)
    icon = "trash"
    rack_id = ""

    # required to prime the remove rack dialog with the rack id
    def get_link_url(self):
        if self.rack_id != "":
            return reverse(self.url, args=[self.rack_id])
        else:
            return self.url

    def allowed(self, request, datum):
        return False  # hide Remove Rack function for now
        __method__ = 'tables.RemoveRackLink.allowed'

        # The Remove Rack button should always be displayed, but we want
        # it to be disabled when there are any resources present.  For now
        # assume button is NOT disabled.
        disable_delete = False
        if self.rack_id != "":
            # list_resources(labels=None, isbriefly=False, device_types=None,
            # resourceids=None, list_device_id=False, is_detail=False,
            # racks=None)
            # Retrieve the resources for the selected rack
            logging.debug("%s: before retrieving resources for rack: %s",
                          __method__, self.rack_id)

            (rc, result_dict) = resource_mgr.list_resources(None, False, None,
                                                            None, False, False,
                                                            [self.rack_id])

            if rc != 0:
                # Unexpected.  Unable to retrieve rack information for selected
                # rack.  Log that fact, and allow the remove rack button to be
                # active
                msg = str('Unable to retrieve Operational Management inventory'
                          ' information for resources.')
                messages.error(request, msg)
                logging.error('%s: Unable to retrieve Operational Management'
                              ' inventory information. A Non-0 return code'
                              ' returned from resource_mgr.list_resources.'
                              ' The return code is: %s', __method__, rc)
            else:
                resources = result_dict['resources']
                # if the rack has any resources associated with it in the
                # inventory don't allow the user to delete it
                logging.debug("%s: got resource info for rack %s.  Number of "
                              "resources for this rack is: %s",
                              __method__, self.rack_id, len(resources))
                if len(resources) > 0:
                    disable_delete = True

        if disable_delete:
            # Add the disabled class to the button (if it's not already
            # there)
            if 'disabled' not in self.classes:
                self.classes = list(self.classes) + ['disabled']
        else:
            # Remove the disabled class from the button (if it's still there)
            if 'disabled' in self.classes:
                self.classes.remove('disabled')
        return True


class ResourceFilterAction(tables.FilterAction):
    name = "resource_filter"

    def filter(self, table, resources, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [resource for resource in resources
                if q in resource.name.lower()]


class NameLinkColumn(tables.Column):
    # Will make the label column a link if there is a web_url associated with
    # the resource. Also ensure the link opens to a new window (that is a
    # unique window for that particular resource)
    def get_link_url(self, datum):
        if datum.web_url:
            self.link_attrs['target'] = datum.name
            return datum.web_url
        else:
            return None


class ResourcesTable(tables.DataTable):
    name = NameLinkColumn('name',
                          verbose_name=_('Label'),
                          link=True)
    type = tables.Column('type',
                         verbose_name=_("Type"))
    arch = tables.Column('arch',
                         verbose_name=("Architecture"))
    capabilities = tables.Column(
        lambda obj: getattr(obj, 'capabilities', []),
        verbose_name=_("Capabilities"),
        hidden=True,
        wrap_list=False,
        filters=(filters.unordered_list,))
    rack_loc = tables.Column('rack_loc',
                             verbose_name=_("EIA Location"))
    userid = tables.Column('userid',
                           verbose_name=_("Management User"))
    mtm = tables.Column('mtm',
                        verbose_name=_("Machine Type/Model"))
    serial_num = tables.Column('sn',
                               verbose_name=_("Serial Number"))
    host_name = tables.Column(
        lambda obj: getattr(obj, 'host_name', []),
        verbose_name=_("Host Name"),
        wrap_list=True,
        filters=(filters.unordered_list,))
    version = tables.Column('version',
                            verbose_name=_("Installed Version"))
    resource_id = tables.Column('resource_id',
                                hidden=True,
                                verbose_name=_("Resource ID"))

    class Meta(object):
        name = "resources"
        verbose_name = _("Resources")
        multi_select = False
        row_actions = (EditResourceLink, ChangePasswordLink,
                       RemoveResourceLink)
        table_actions = (ResourceFilterAction, AddResourceLink)
        # table_actions = (ResourceFilterAction, AddResourceLink,
        #                  RemoveResources)


class RackDetailsTable(tables.DataTable):
    # This is a generic table (id, label/title, value)
    row_title = tables.Column('row_title',
                              attrs={'width': '150px', },
                              verbose_name=_("Rack Property"))
    row_value = tables.Column('row_value',
                              attrs={'width': '400px', },
                              verbose_name=_("Value"))

    class Meta(object):
        name = "rack_details"
        verbose_name = _("Rack Details")
        multi_select = False
        footer = False
        filter = False
        # Until we have Add Rack function, we don't allow
        # remove rack to be present (Remove Rack is hidden
        # via its 'allowed' function)
        table_actions = (EditRackLink, RemoveRackLink)
