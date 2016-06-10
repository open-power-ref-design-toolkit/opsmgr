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

from django.conf.urls import patterns
from django.conf.urls import url

from operational_mgmt.inventory import views

urlpatterns = patterns(
    'operational_mgmt.inventory.views',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<resource_id>[^/]+)/update/$',
        views.EditResourceView.as_view(), name='editResource'),
    url(r'^(?P<resource_id>[^/]+)/chpwd/$',
        views.ChangePasswordView.as_view(), name='changePassword'),
    url(r'^(?P<rack_id>[^/]+)/addResource/$',
        views.AddResourceView.as_view(), name='addResource'),
    url(r'^(?P<rack_id>[^/]+)/edit_rack/$',
        views.EditRackView.as_view(), name='editRack'),
    url(r'^(?P<rack_id>[^/]+)/removeRack/$',
        views.RemoveRackView.as_view(), name='removeRack'),
    url(r'^(?P<resource_id>[^/]+)/removeResource/$',
        views.RemoveResourceView.as_view(), name='removeResource'),
    url(r'^(?P<rack_id>[^/]+)/removeResources/$',
        views.RemoveResourcesView.as_view(), name='removeResources'))
