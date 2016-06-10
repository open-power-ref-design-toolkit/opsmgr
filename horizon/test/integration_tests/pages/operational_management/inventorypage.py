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

from openstack_dashboard.test.integration_tests.pages import basepage
from openstack_dashboard.test.integration_tests.regions import forms
from openstack_dashboard.test.integration_tests.regions import tables
from selenium.webdriver.common import by
from selenium.webdriver.support.ui import Select


# Defines the form fields and actions that are associated with the 
# the resources table on the Inventory page
class ResourcesTable(tables.TableRegion):
    name = 'resources'
    ADD_RESOURCE_FORM_FIELDS = ("label", "eiaLocation", "ip_address",
                               "userID", "password")
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

    @tables.bind_row_action('removeResource')
    def remove_resource(self, remove_button, row):
        remove_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)

    @tables.bind_row_action('changePassword')
    def change_password(self, change_password_button, row):
        change_password_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.CHANGE_PASSWORD_FORM_FIELDS)

    @tables.bind_row_action('editRack')
    def edit_rack(self, edit_button):
        edit_button.click()
        return forms.BaseFormRegion(self.driver, self.conf,
                                    field_mappings=self.EDIT_RACK_FORM_FIELDS)


# Defines the form fields and actions that are associated with the 
# the resources table on the Inventory page
class RackDetailsTable(tables.TableRegion):
    name = 'rack_details'
    EDIT_RACK_FORM_FIELDS = ("label", "data_center", "room", "row", "notes")

    @tables.bind_table_action('editRack')
    def edit_rack(self, edit_rack_button):
        edit_rack_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.EDIT_RACK_FORM_FIELDS)


class InventoryPage(basepage.BaseNavigationPage):
    RESOURCES_TABLE_NAME_COLUMN = 'name'
    _application_selector_locator = (by.By.ID, 'applicationSelector')
    _application_launch_button_locator = (by.By.ID, 'appLaunchButton')
    # rack details link id starts with "rackDetailsLink" -- and then 
    # has a uniqifier at the end.  So use the correct syntax to get 
    # the item whose id starts with 'rackDetailsLink'
    _rack_details_locator = (by.By.CSS_SELECTOR, 'a[id^="rackDetailsLink"]')

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
        rackDetails = self._get_element(*self._rack_details_locator)
        # open rack details section
        rackDetails.click()
        # perform edit rack
        edit_rack_form = self.rack_details_table.edit_rack()
        edit_rack_form.label.text = new_label
        edit_rack_form.data_center.text = data_center
        edit_rack_form.room.text = room
        edit_rack_form.row.text = row
        edit_rack_form.notes.text = notes
        edit_rack_form.submit()

    def add_resource(self, name, eiaLocation, ip_address,
                    userID, password):
        # Perform the add resource
        add_resource_form = self.resources_table.add_resource()
        add_resource_form.label.text = name
        add_resource_form.eiaLocation.text = eiaLocation
        add_resource_form.ip_address.text = ip_address
        add_resource_form.userID.text = userID
        add_resource_form.password.text = password
        add_resource_form.submit()

    def edit_resource(self, name, new_name, eiaLocation, ip_address,
             auth_method, userID, password, sshKey, passphrase):
        # find the resource that needs to be edited
        row = self._get_row_with_resource_name(name)
        # perform edit resource
        edit_form = self.resources_table.edit_resource(row)
        edit_form.label.text = new_name
        edit_form.eiaLocation.text = eiaLocation
        edit_form.ip_address.text = ip_address
        edit_form.auth_method.value = auth_method
        # based on authentication method selected, fill in the
        # visible fields
        if (auth_method == u'1'):
            edit_form.userID.text = userID   
            edit_form.sshKey.text = sshKey
            edit_form.passphrase.text = passphrase
        else:
            edit_form.userID.text = userID
            edit_form.password.text = password
        edit_form.submit()

    def remove_resource(self, name):
        # find the resource that needs to be removed
        row = self._get_row_with_resource_name(name)
        # perform the remove
        confirm_delete_resource_form = self.resources_table.remove_resource(row)
        confirm_delete_resource_form.submit()

    def change_password(self, name, userID, oldpassword, password, confirm_password):
        # find the resource where the user's password needs to be changed
        row = self._get_row_with_resource_name(name)
        # perform the change password
        change_password_form = self.resources_table.change_password(row)
        change_password_form.oldpassword.text = oldpassword
        change_password_form.password.text = password
        change_password_form.confirm_password.text = confirm_password
        change_password_form.submit()

    def launch_application(self, application):
        # find the launch application button to activate
        appLaunchButton = self._get_element(*self._application_launch_button_locator)
        # find the application selector at the top of the page
        appSelector = self._get_element(*self._application_selector_locator)
        # Access the app selector
        dropdown = Select(appSelector)
        # Choose the correct option in the selector
        dropdown.select_by_value(application)
        # Perform the launch
        appLaunchButton.click()


    def is_resource_present(self, name):
        return bool(self._get_row_with_resource_name(name))

    def _get_row_with_resource_name(self, name):
        return self.resources_table.get_row(self.RESOURCES_TABLE_NAME_COLUMN, name)
