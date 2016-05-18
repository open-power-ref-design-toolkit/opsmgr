from django.utils.translation import ugettext_lazy as _

from horizon import messages
from horizon import tabs

import logging

from openstack_dashboard.dashboards.operational_mgmt.inventory import tables
from openstack_dashboard.dashboards.operational_mgmt import rack
from openstack_dashboard.dashboards.operational_mgmt import resource

import opsmgr.inventory.device_mgr as device_mgr
import opsmgr.inventory.plugins as plugins


class RowEntry(object):
    # The class "constructor" - It's actually an initializer
    def __init__(self, row_id, row_title, row_value):
        self.id = row_id
        self.row_title = row_title
        self.row_value = row_value


def make_generic_row(row_id, row_title, row_value):
    return RowEntry(row_id, row_title, row_value)


class AppLinkEntry(object):
    # The class "constructor" - It's actually an initializer
    def __init__(self, row_id, app_name, protocol, port, path):
        self.id = row_id
        self.app_name = app_name
        self.protocol = protocol
        self.port = port
        self.path = path


def make_app_link_row(row_id, app_name, protocol, port, path):
    return AppLinkEntry(row_id, app_name, protocol, port, path)


def retrieve_rack_resources(self):
    # retrieve resources for the rack id passed in (rack_id may be -1 on
    # the initial pass)
    __method__ = 'tabs.retrieve_rack_resources'
    devices = []

    logging.debug("%s: before retrieving resources for rack: %s",
                  __method__, self.rack_id)

    (rc, result_dict) = device_mgr.list_devices(None, False, None, None,
                                                False, False, [self.rack_id])
    if rc != 0:
        messages.error(self.request, _('Unable to retrieve Operational'
                                       ' Management inventory information'
                                       ' for resources.'))
        logging.error('%s: Unable to retrieve Operational Management'
                      'inventory information. A Non-0 return code returned'
                      ' from device_mgr.list_devices.  The return code is:'
                      ' %s', __method__, rc)
    else:
        all_devices = result_dict['devices']
        for raw_device in all_devices:
            devices.append(resource.Resource(raw_device))

    logging.debug("%s: Found %s resources",
                  __method__, len(devices))
    return devices


def retrieve_rack_metadata(self):
    # retrieve the rack details for the rack passed in (rack_id may be -1 on
    # initial pass)
    __method__ = 'tabs.retrieve_rack_metadata'
    rack_meta_data = []
    (rc, result_dict) = device_mgr.list_racks(None, False, [self.rack_id])

    if rc != 0:
        messages.error(self.request, _('Unable to retrieve Operational'
                                       ' Management inventory information'
                                       ' for racks.'))
        logging.error('%s, Unable to retrieve Operational Management'
                      ' inventory information. A Non-0 return code returned'
                      ' from device_mgr.list_racks.  The return code is:'
                      ' %s', __method__, rc)
    else:
        # We should have at least one resource in the results...just return
        # the metadata for the first value
        if len(result_dict['racks']) > 0:
            the_rack = rack.Rack(result_dict['racks'][0])
            counter = 0
            rack_meta_data.append(make_generic_row(counter, "Label",
                                                   the_rack.name))
            counter += 1
            rack_meta_data.append(make_generic_row(counter, "Data Center",
                                                   the_rack.data_center))
            counter += 1
            rack_meta_data.append(make_generic_row(counter, "Location",
                                                   the_rack.rack_loc))
            counter += 1
            rack_meta_data.append(make_generic_row(counter, "Notes",
                                                   the_rack.notes))
    return rack_meta_data


def retrieve_application_links(self):
    link_data = []

    # Retrieve the applications' link information
    applications = plugins.get_operations_plugins()

    counter = 0
    for app in applications:
        link_data.append(make_app_link_row(counter, app.name, app.protocol,
                                           app.port, app.path))
        counter += 1

    return link_data


class RackTabBase(tabs.TableTab):
    table_classes = (tables.RackDetailsTable, tables.ResourcesTable,
                     tables.ServerLinksTable)
    template_name = ("op_mgmt/inventory/rack_tab.html")
    preload = False
    _has_more = False
    rack_fields = []
    rack_id = -1

    def get_resources_data(self):
        # Store the rack_id of the current rack into
        # the AddResource action
        tables.AddResourceLink.rack_id = self.rack_id
        # Return the list of resources
        return retrieve_rack_resources(self)

    def get_rack_details_data(self):
        # Store the rack_id of the current rack into each action that
        # needs it
        tables.EditRackLink.rack_id = self.rack_id
        tables.RemoveRackLink.rack_id = self.rack_id
        return retrieve_rack_metadata(self)

    def get_application_links_data(self):
        return retrieve_application_links(self)


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
        __method__ = 'tabs.InventoryRacksTabs.__init__'
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
        logging.debug("%s: before retrieving rack all racks",
                      __method__)
        (rc, result_dict) = device_mgr.list_racks()
        if rc != 0:
            messages.error(self.request, _('Unable to retrieve Operational'
                                           ' Management inventory information'
                                           ' for racks.'))
            logging.error('%s: Unable to retrieve Operational Management'
                          ' inventory information. A Non-0 return code'
                          ' returned from device_mgr.list_racks.  The'
                          ' return code is: %s', __method__, rc)
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

            logging.debug("%s: creating a new tab for rack with label: %s",
                          __method__, a_rack['label'])

        #  end loop through each rack

        # clear out that default tab from the tab group
        self._tabs.clear()
        # update the tab group with the list of defined tabs
        self._tabs.update(defined_tabs)
        # update tabs with the list of tab classes
        self.tabs = tuple(list_tabs)
