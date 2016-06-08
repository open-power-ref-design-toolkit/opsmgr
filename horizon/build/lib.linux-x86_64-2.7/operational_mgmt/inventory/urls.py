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
        views.RemoveResourceView.as_view(), name='removeResource'))
