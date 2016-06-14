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
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,A019CCF70FBCE51F86FB8FDCC44FE188

MKmP7J811ya5oUtErpWZp5Wgorpi/h4cfCxxsiMvestnR1MeT3OGvmTyWjZuAYKR
3vJOOnDDOOe+pMWcSzZGbsKjuNOkhrUfgVb3nUngoVjkb7mWY5aErkEBrK5gWhZj
0BFH8e0yXslQlhul5He9gXqf01ncwZf+zWJ3DoyXGJ2iYimif+esJt1Vk5r0NX6n
cNe3ME1OJ/ScVBxrdvB0/T5M0rpIJQz/FdhzXwMDzZ0eJi8dE5unHRjLL0VFxW7z
tnD6BdM/VpZumjgTB/NdpiWUlfYG5dVIvLCD1yOWtF/8HmTlTllYMET/ZDYFQReH
TzY5BQFfnIIYAm71lMjGIdbt4YQeoj+mRN50zhaAQjpH2MQR8Yaj+8L89dkw8s31
ZkFCVw88HIG2F4zSV1BUPueYyFm2/ahy7pEN1dvYXgsEYG0je9Z9Gufhi0VNM0qD
IEkTYnzDk+T+qJaQllzZH+663VsD40TasYI4AFNdmrw78OjUSGD/e+xfqYnmk7p/
Homhw2ZpRq7/wNCfImaE39ESZc7Bg5EGGyXx9gTchD+4i9SRzNCWmgCtX5VSdyp4
a5NsVVyt1+MNTzdKGL1jI0M4GYU3i9ITbi9EPVS6PlaJU7dnXgFpT55gg7UIvNFy
OoOLzL6+GaOgs1AB7rJLe02ZWoeof0sb084LJx3rFnI7a0/8iH9IKEuAudmU3eN7
2IAnrI1w0DgX5jDu2ZJquwGKoBF4u9RSz4S1jd5GBK7aDR/OoqQdEQe3jwndgoq6
ZJsiSwz/LG4DsHqgT4qxMgDN2IUixGlTH4GZ85Jz/7L294jBaUmAGlfZ8Lsu/v+b
D/PsrOThwPza1SZAFDfchYmM8esMZ1lSSs0/65nJR7i1DJdUfCgWMkl28QpHEK57
q3lTSXkR6kMTrPAL+E5afyc6HcL1vQVZmv4WRMKIJfUIbebv1ISpe1kagJLYei6t
7OCODbxt8FrjnrmnBlVQbIASA64mTftY/9Jhf4GwIFGMaP9KlR7qe8VKX3JgipEd
9sX1I7+efc6vzV+x6YsDYy9IXtSyOGsQKAoJSvCPJMHlbs7g0b9fK+icCREhA/Cd
sG8mMilcggAPYJHQMayj2zK8hB498BCS8CBCLwhfJiBlVSVahBC8x7ZAhnPSO12U
PZSWodamybmDsnWUKkD/4hWyEafgOnckt5UAHdlapmQlDp9969Z2TYxdhZ9uSX5V
OI86+n7cd9hrCJAqn9oDCzZK2RT54k57Sf8XRy0dld3vxLqoxfJxiwVtwNnYA1oI
4dYWrEuC7TPLvpzFIEltOUiCTzpsATPVVjL90S3gbcgKRHtAKGDVQMJjI/7vAlj/
uNjthZCdGQZSoz2mwNbnwtocOwN4ZUnuhAlVTLnHAoqvryWmxNLtiWAiqQMmBUzH
D92e0ZC4KX0dgRqY30Nt4pzfS+ILUhSy1yg8SNyZ477e2njOHYJ28WI2ujpEd3Fj
KmM+NdVIvSEOZJUF9FgoOfW82OH7h/tLxPOZgC1enoL1tU0C4ZMnLbh0Y3TiuZ3K
jYeOtp0Xk/uU2g03fizO0NIg09CenygUCkoncidU0Ze/RGV8+W2SGYMqoyCOFXxp
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
    SSH_AUTH_METHOD = u'1'
    NEW_RESOURCE_NAME = "UPDATED"
    NEW_RACK_NAME = "Rack1_Updated"
    NEW_DATA_CENTER = "new data-center"
    NEW_ROOM = "new room"
    NEW_ROW = "new row" 
    NEW_NOTES = "These notes are updated"

    def test_inventory(self):
        # Go to inventory page
        inv_page = self.home_pg.go_to_operationalmanagement_inventorypage()
        return    #  Just skip over the location-specific tests

        # Open rack details and edit them
        inv_page.edit_rack(self.NEW_RACK_NAME, self.NEW_DATA_CENTER,
                           self.NEW_ROOM, self.NEW_ROW, self.NEW_NOTES)
        self.assertTrue(inv_page.find_message_and_dismiss(
                        messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss(
                         messages.ERROR))

        # Attempt to add a resource by localhost (should succeed)
        inv_page.add_resource(self.HOST_RESOURCE_NAME, self.HOST_EIA,
                              self.HOST_NAME, self.HOST_USERID,
                              self.INITIAL_PASSWORD)
        self.assertTrue(inv_page.find_message_and_dismiss(
                        messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss(
                         messages.ERROR))

        # Verify the resource exists
        self.assertTrue(inv_page.is_resource_present(
                        self.HOST_RESOURCE_NAME))

        # Attempt to add the resource a second time (should fail)
        # inv_page.add_resource(self.HOST_RESOURCE_NAME, self.HOST_EIA,
        #                      self.HOST_NAME, self.HOST_USERID,
        #                      self.INITIAL_PASSWORD)
        # self.assertTrue(inv_page.find_message_and_dismiss(
        #                messages.ERROR))
        # self.assertFalse(inv_page.find_message_and_dismiss(
        #                 messages.SUCCESS))

        # Attempt to remove the resource (should succeed)
        inv_page.remove_resource(self.HOST_RESOURCE_NAME)
        self.assertTrue(inv_page.find_message_and_dismiss(
                        messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss(
                         messages.ERROR))

        # Verify the resource no longer exists
        self.assertFalse(inv_page.is_resource_present(
                         self.HOST_RESOURCE_NAME))

        # Attempt to add a resource a resource by IP address
        # (should succeed)
        inv_page.add_resource(self.IP_RESOURCE_NAME, self.IP_EIA,
                              self.IP_ADDRESS, self.IP_USERID,
                              self.INITIAL_PASSWORD)
        self.assertTrue(inv_page.find_message_and_dismiss(
                        messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss(
                         messages.ERROR))

        # Verify the resource exists
        self.assertTrue(inv_page.is_resource_present(
                        self.IP_RESOURCE_NAME))

        # Attempt to change the password for the user on that resource
        # (should succeed)
        inv_page.change_password(self.IP_RESOURCE_NAME, self.IP_USERID,
                                 self.INITIAL_PASSWORD, self.NEW_PASSWORD,
                                 self.NEW_PASSWORD)
        self.assertTrue(inv_page.find_message_and_dismiss
                        (messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss
                         (messages.ERROR))

        # Attempt to edit the resource
        # (change auth method: so sshkey/passphrase)
        inv_page.edit_resource(self.IP_RESOURCE_NAME,
                               self.NEW_RESOURCE_NAME,
                               self.IP_EIA2, self.IP_ADDRESS,
                               self.SSH_AUTH_METHOD, self.IP_USERID2,
                               "", self.SSH_KEY, self.PASSPHRASE)
        self.assertTrue(inv_page.find_message_and_dismiss
                        (messages.SUCCESS))
        self.assertFalse(inv_page.find_message_and_dismiss
                         (messages.ERROR))

        # Verify the resource exists (by its new name)
        self.assertTrue(inv_page.is_resource_present
                        (self.NEW_RESOURCE_NAME))

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
