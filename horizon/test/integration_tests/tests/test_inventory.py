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

from openstack_dashboard.test.integration_tests import helpers
from openstack_dashboard.test.integration_tests.regions import messages


class TestInventory(helpers.OpsMgrTestCase):
    """These are the test scenarios:
    * > checks that the inventory page is available
    * > checks that the inventory page loads without error
    * > checks that the rack details can be edited
    * > adds a resource by host name
    * > checks that a resource can be removed
    * > adds a resource by IP address
    * > changes the password of a user on a resource
    * > edits a resource to change authentication
    * > checks that a launching into each application is possible
    """
    RESOURCE_NAME = helpers.gen_random_resource_name("resource")

    # Additional test constants that will need to be changed based
    # on the test environment
    HOST_RESOURCE_NAME = "hostname_" + RESOURCE_NAME
    IP_RESOURCE_NAME = "ip_" + RESOURCE_NAME
    HOST_NAME = "localhost"
    IP_ADDRESS = "x.xx.xx.xx"
    SSH_KEY = """-----BEGIN RSA PRIVATE KEY-----
-----END RSA PRIVATE KEY-----"""
    INITIAL_PASSWORD = "xxxxxxx"
    PASSPHRASE = "xxxxxxxx"
    NEW_PASSWORD = "xxxxxxxx"
    HOST_USERID = "xxxxxx"
    IP_USERID = "xxxxxx"
    IP_USERID2 = "xxxxx"
    HOST_EIA = "12U"
    IP_EIA = "19U"
    IP_EIA2 = "13U"
    PWD_AUTH_METHOD = u'0'
    SSH_AUTH_METHOD = u'1'
    NEW_RESOURCE_NAME = "UPDATED"
    NEW_RACK_NAME = "Rack1_Updated"
    NEW_DATA_CENTER = "new data-center"
    NEW_ROOM = "new room"
    NEW_ROW = "new row"
    NEW_NOTES = "These notes are updated"

    class SecurityInfo(object):
        def __init__(self, auth_method, user_id, password, ssh_key,
                     passphrase):
            self.auth_method = auth_method
            self.user_id = user_id
            self.password = password
            self.ssh_key = ssh_key
            self.passphrase = passphrase

    def test_inventory(self):
        # Go to inventory page
        inv_page = self.home_pg.go_to_operationalmanagement_inventorypage()
        return    # Just skip over the location-specific tests

        # Open rack details and edit them
        inv_page.edit_rack(self.NEW_RACK_NAME, self.NEW_DATA_CENTER,
                           self.NEW_ROOM, self.NEW_ROW, self.NEW_NOTES)
        self.assertTrue(inv_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss(messages.ERROR))

        # Attempt to add a resource by localhost (should succeed)
        security_info = self.SecurityInfo(self.PWD_AUTH_METHOD,
                                          self.HOST_USERID,
                                          self.INITIAL_PASSWORD, "", "")
        inv_page.add_resource(self.HOST_RESOURCE_NAME, self.HOST_EIA,
                              self.HOST_NAME, security_info)
        self.assertTrue(inv_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss(messages.ERROR))

        # Verify the resource exists
        self.assertTrue(inv_page.is_resource_present(self.HOST_RESOURCE_NAME))

        # Verify the resource is using password authentication
        self.assertTrue(
            inv_page.is_auth_method_set(self.HOST_RESOURCE_NAME, 0))

        # Attempt to add the resource a second time (should fail)
        # inv_page.add_resource(self.HOST_RESOURCE_NAME, self.HOST_EIA,
        #                      self.HOST_NAME, security_info)
        # self.assertTrue(inv_page.find_message_and_dismiss(
        #                messages.ERROR))
        # self.assertFalse(inv_page.find_message_and_dismiss(
        #                 messages.SUCCESS))

        # Attempt to remove the resource (should succeed)
        inv_page.remove_resource(self.HOST_RESOURCE_NAME)
        self.assertTrue(inv_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss(messages.ERROR))

        # Verify the resource no longer exists
        self.assertFalse(inv_page.is_resource_present(self.HOST_RESOURCE_NAME))

        # Attempt to add a resource a resource by IP address
        # (should succeed)
        security_info = self.SecurityInfo(self.SSH_AUTH_METHOD,
                                          self.IP_USERID2, "", self.SSH_KEY,
                                          self.PASSPHRASE)

        inv_page.add_resource(self.IP_RESOURCE_NAME, self.IP_EIA,
                              self.IP_ADDRESS, security_info)
        self.assertTrue(inv_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss(messages.ERROR))

        # Verify the resource exists
        self.assertTrue(inv_page.is_resource_present(self.IP_RESOURCE_NAME))

        # Verify the resource is using sshkey authentication
        self.assertTrue(inv_page.is_auth_method_set(self.IP_RESOURCE_NAME, 1))

        # Attempt to edit the resource
        # (change auth method: so sshkey/passphrase)
        security_info = self.SecurityInfo(self.PWD_AUTH_METHOD,
                                          self.IP_USERID,
                                          self.INITIAL_PASSWORD, "", "")

        inv_page.edit_resource(self.IP_RESOURCE_NAME, self.NEW_RESOURCE_NAME,
                               self.IP_EIA2, self.IP_ADDRESS, security_info)
        self.assertTrue(inv_page.find_message_and_dismiss
                        (messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss
                         (messages.ERROR))

        # Verify the resource exists (by its new name)
        self.assertTrue(inv_page.is_resource_present
                        (self.NEW_RESOURCE_NAME))

        # Verify the resource is now PWD authentication
        self.assertTrue(inv_page.is_auth_method_set(self.NEW_RESOURCE_NAME, 0))

        # Attempt to change the password for the user on that resource
        # (should succeed)
        inv_page.change_password(self.NEW_RESOURCE_NAME, self.INITIAL_PASSWORD,
                                 self.NEW_PASSWORD, self.NEW_PASSWORD)
        self.assertTrue(inv_page.find_message_and_dismiss
                        (messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss
                         (messages.ERROR))

        # Attempt to remove the updated resource (should succeed)
        inv_page.remove_resource(self.NEW_RESOURCE_NAME)
        self.assertTrue(inv_page.find_message_and_dismiss
                        (messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss
                         (messages.ERROR))

        # Attempt to launch logging application
        inv_page.launch_application("logging::elk")

        # Attempt to launch monitoring application
        inv_page.launch_application("monitoring::nagios")
