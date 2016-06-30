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

from openstack_dashboard.test.integration_tests.pages import basepage
from openstack_dashboard.test.integration_tests.regions import forms
from openstack_dashboard.test.integration_tests.regions import tables
from selenium.webdriver.common import by
from selenium.webdriver.support.ui import Select


class ResourcesTable(tables.TableRegion):
    # Defines the form fields and actions that are associated with the
    # the resources table on the Inventory page
    name = 'resources'
    ADD_RESOURCE_FORM_FIELDS = ("label", "eiaLocation", "ip_address",
                                "auth_method", "userID", "password", "sshKey",
                                "passphrase")
    EDIT_RESOURCE_FORM_FIELDS = ("label", "eiaLocation", "ip_address",
                                 "auth_method", "userID", "password", "sshKey",
                                 "passphrase")
    CHANGE_PASSWORD_FORM_FIELDS = ("userID", "label", "oldpassword",
                                   "password", "confirm_password")
    EDIT_RACK_FORM_FIELDS = ("label", "data_center", "room", "row", "notes")

    @tables.bind_table_action('addResource')
    def add_resource(self, add_button):
        add_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.ADD_RESOURCE_FORM_FIELDS)

    @tables.bind_row_action('edit', primary=True)
    def edit_resource(self, edit_button, row):
        edit_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.EDIT_RESOURCE_FORM_FIELDS)

    @tables.bind_row_action('RemoveResourceAction')
    def remove_resource(self, remove_button, row):
        remove_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)

    @tables.bind_row_action('changePassword')
    def change_password(self, change_password_button, row):
        change_password_button.click()
        return forms.FormRegion(
            self.driver, self.conf,
            field_mappings=self.CHANGE_PASSWORD_FORM_FIELDS)


class RackDetailsTable(tables.TableRegion):
    # Defines the form fields and actions that are associated with the
    # the resources table on the Inventory page
    name = 'rack_details'
    EDIT_RACK_FORM_FIELDS = ("label", "data_center", "room", "row", "notes")

    @tables.bind_table_action('editRack')
    def edit_rack(self, edit_rack_button):
        edit_rack_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.EDIT_RACK_FORM_FIELDS)


class InventoryPage(basepage.BaseNavigationPage):
    RESOURCES_TABLE_NAME_COLUMN = 'name'
    _application_selector_locator = (by.By.ID, 'capabilitiesSelector')
    _app_launch_button_locator = (by.By.ID, 'capLaunchButton')
    # rack details link id starts with "rackDetailsLink" -- and then
    # has a uniqifier at the end.  So use the correct syntax to get
    # the item whose id starts with 'rackDetailsLink'
    _rack_details_locator = (by.By.CSS_SELECTOR, 'a[id^="rackDetailsLink"]')
    _password_field_locator = (by.By.ID, 'id_password')
    _sshkey_field_locator = (by.By.ID, 'id_sshKey')

    def __init__(self, driver, conf):
        super(InventoryPage, self).__init__(driver, conf)
        self._page_title = "Inventory"

    @property
    def resources_table(self):
        return ResourcesTable(self.driver, self.conf)

    @property
    def rack_details_table(self):
        return RackDetailsTable(self.driver, self.conf)

    def edit_rack(self, new_label, data_center, room, row, notes):
        # find the rack details section
        rack_details = self._get_element(*self._rack_details_locator)
        # open rack details section
        rack_details.click()
        # perform edit rack
        edit_rack_form = self.rack_details_table.edit_rack()
        edit_rack_form.label.text = new_label
        edit_rack_form.data_center.text = data_center
        edit_rack_form.room.text = room
        edit_rack_form.row.text = row
        edit_rack_form.notes.text = notes
        edit_rack_form.submit()

    def add_resource(self, name, eia_location, ip_address, security_info):
        # Perform the add resource
        add_resource_form = self.resources_table.add_resource()
        add_resource_form.label.text = name
        add_resource_form.eiaLocation.text = eia_location
        add_resource_form.ip_address.text = ip_address
        add_resource_form.auth_method.value = security_info.auth_method

        # based on authentication method passed in, fill in the
        # visible fields
        if security_info.auth_method == u'1':
            add_resource_form.userID.text = security_info.user_id
            add_resource_form.sshKey.text = security_info.ssh_key
            add_resource_form.passphrase.text = security_info.passphrase
        else:
            add_resource_form.userID.text = security_info.user_id
            add_resource_form.password.text = security_info.password
        add_resource_form.submit()

    def is_auth_method_set(self, name, auth_method):
        # find the resource that we need to check
        row = self._get_row_with_resource_name(name)

        # open edit resource dialog on the item
        edit_form = self.resources_table.edit_resource(row)

        # check the authentication method for the page
        if int(edit_form.auth_method.value) == int(auth_method):
            edit_form.cancel()
            return True
        else:
            edit_form.cancel()
            return False

    def edit_resource(self, name, new_name, eia_location, ip_address,
                      security_info):
        # find the resource that needs to be edited
        sel_row = self._get_row_with_resource_name(name)
        # perform edit resource
        edit_form = self.resources_table.edit_resource(sel_row)
        edit_form.label.text = new_name
        edit_form.eiaLocation.text = eia_location
        edit_form.ip_address.text = ip_address
        edit_form.auth_method.value = security_info.auth_method

        # based on authentication method passed in, fill in the
        # visible fields (setting the auth method should force the
        # following fields to be displayed).
        if security_info.auth_method == u'1':
            edit_form.userID.text = security_info.user_id
            edit_form.sshKey.text = security_info.ssh_key
            edit_form.passphrase.text = security_info.passphrase
        else:
            edit_form.userID.text = security_info.user_id
            edit_form.password.text = security_info.password
        edit_form.submit()

    def remove_resource(self, name):
        # find the resource that needs to be removed
        sel_row = self._get_row_with_resource_name(name)
        # perform the remove
        conf_dlt_resource_form = self.resources_table.remove_resource(sel_row)
        conf_dlt_resource_form.submit()

    def change_password(self, name, oldpassword, password,
                        confirm_password):
        # find the resource where the user's password needs to be changed
        sel_row = self._get_row_with_resource_name(name)
        # perform the change password
        change_password_form = self.resources_table.change_password(sel_row)
        change_password_form.oldpassword.text = oldpassword
        change_password_form.password.text = password
        change_password_form.confirm_password.text = confirm_password
        change_password_form.submit()

    def launch_application(self, application):
        # find the launch application button to activate
        app_launch_button = self._get_element(
            *self._app_launch_button_locator)
        # find the application selector at the top of the page
        app_selector = self._get_element(*self._application_selector_locator)
        # Access the app selector
        dropdown = Select(app_selector)
        # Choose the correct option in the selector
        dropdown.select_by_value(application)
        # Perform the launch
        app_launch_button.click()

    def is_resource_present(self, name):
        return bool(self._get_row_with_resource_name(name))

    def _get_row_with_resource_name(self, name):
        return self.resources_table.get_row(self.RESOURCES_TABLE_NAME_COLUMN,
                                            name)
