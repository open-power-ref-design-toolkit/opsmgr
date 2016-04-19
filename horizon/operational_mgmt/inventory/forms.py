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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

import opsmgr.inventory.device_mgr as device_mgr
from openstack_dashboard.dashboards.operational_mgmt.inventory \
    import tabs as inventoryRacks_tabs

import logging
import pdb
def create_rack_choices():
    rackChoices = []
    (rc2, result_dict) = device_mgr.list_racks() 

    if rc2!=0:
       messages.error(self.request, _('Unable to retrieve Operational Management inventory information for rack extensions.'))
       logging.error('Unable to retrieve Operational Management rack inventory information.'
                     'A Non-0 return code returned from device_mgr.list_racks.  The return code is: %s' % rc)
    else:
       value = result_dict['racks']
       for s in value:
          rackChoices.append((s['rackid'], s['label']))
    return rackChoices

class AddResourceForm(forms.SelfHandlingForm):
    label = forms.CharField(label=_("Label"),
                                  max_length=255,
                                  required=True)
    rackid = forms.ChoiceField(label=_("Rack"), 
                                required = True)   
    eiaLocation = forms.CharField(label=_("EIA Location"),
                                  max_length=3,
                                  required=False)
    ip_address = forms.IPField(label=_("IP Address"),
                                  version=forms.IPv4,
                                  required=True, mask=False)
    # If no initial value is provided on user ID, Chrome wants to prime with a saved userid
    # and prime the password, too -- so give it a space...
    userID = forms.CharField(label=_("User ID"),
                                  initial=_(" "),
                                  max_length=255,
                                  required=True)

#    pwdBool = forms.BooleanField(label=_("Password Required"),
#                                 initial=True, required=False,
#                                 widget=forms.CheckboxInput(attrs={
#                                 'data-slug': 'pwd'}))

    password = forms.CharField(widget= forms.PasswordInput(render_value=False),
                               required=False)
#    pdb.set_trace()
#    password = forms.CharField(label = _("password2"), widget=forms.PasswordInput
#                                     (attrs={'class': 'switched',
#                                             'data-switch-on': 'pwd',
#                                             'data-pwd': False},
#                                             render_value=False))

#works    pwdRequired = forms.ChoiceField(label=_('Password'),
#                                     choices=[('required', _('Required')),
#                                              ('not_required', _('Not Required'))],
#                                     widget=forms.Select
#                                     (attrs={'class': 'switchable',
#                                             'data-slug': 'pwd'}))
#works    password2 = forms.CharField(label = _("password2"), required=True,
#                                     widget=forms.PasswordInput
#                                     (attrs={'class': 'switched',
#                                             'data-switch-on': 'pwd',
#                                             'data-pwd-required': _("")},
#                                             render_value=False))


# noise   password = forms.CharField(widget= forms.PasswordInput(attrs={
#                                   'class': 'switchable switched',
#                                   'data-switch-on': 'pwdRequired',
#                                   'data-pwdRequired-required': 'test ',},
#                                   render_value=False))

    def __init__(self, request, *args, **kwargs):
        super(AddResourceForm, self).__init__(request, *args, **kwargs)  
        self.fields['rackid'].choices = create_rack_choices()

    def handle(self, request, data):
        try:
#            pdb.set_trace()
            (rc, result_dict) = device_mgr.add_device(data['label'], None, data['ip_address'], data['userID'].strip(), data['password'], data['rackid'], data['eiaLocation'], None)

            if rc!=0:
               msg = _('Attempt to add resource "%s" was not successful. Details of the attempt: "%s"' % (data['label'], result_dict))
               messages.error(request, msg)
            else:
               msg = _('Resource "%s" successfully added.' % data['label'])
               messages.info(request, msg)
            return True
        except Exception as e:
            exceptions.handle(request,
                              _('Unable to add resource.'))

class EditResourceForm(forms.SelfHandlingForm):
    label = forms.CharField(label=_("Label"),
                                  max_length=255,
                                  required=True)
    rackid = forms.ChoiceField(label=_("Rack"), 
                                required = True)
    eiaLocation = forms.CharField(label=_("EIA Location"),
                                  max_length=3,
                                  required=False)
    ip_address = forms.IPField(label=_("IP Address"),
                                  version=forms.IPv4,
                                  required=True, mask=False)
    userID = forms.CharField(label=_("User ID"),
                                  max_length=255,
                                  required=True)
    password = forms.CharField(widget= forms.PasswordInput(render_value=False),
                               required=False)

    def __init__(self, request, *args, **kwargs):
        super(EditResourceForm, self).__init__(request, *args, **kwargs)       
        self.fields['rackid'].choices = create_rack_choices()

    def handle(self, request, data):
        try:            
            (rc, result_dict) = device_mgr.change_device_properties(None, self.initial['deviceId'], data['label'], data['userID'], data['password'], data['ip_address'], data['rackid'], data['eiaLocation'], None)
            if rc!=0:
               # failure case -- so use the initial label for logging/message
               msg = _('Attempt to edit resource "%s" was not successful. Details of the attempt: "%s"' % (self.initial['label'], result_dict))
               messages.error(request, msg)
               logging.error('Unable to edit resource "%s".  Return code "%s" received.  Details of the failure: "%s"' % (self.initial['label'], rc, result_dict))
            else:
               # must have a 0 rc -- display completion msg -- use current label for message
               msg = _('Resource "%s" successfully edited.' % data['label'])
               messages.info(request, msg)
            return True
        except Exception:
            exceptions.handle(request, _('Unable to edit selected resource.'))

class EditRack(forms.SelfHandlingForm):
    label = forms.CharField(label=_("Label"),
                                  max_length=255,
                                  required=True)
    data_center = forms.CharField(label=_("Data Center"),
                                  max_length=255)
    location = forms.CharField(label=_("Location"),
                                  max_length=255,
                                  required=True)
    notes = forms.CharField(label=_("Notes"),
                                  max_length=255)
    def handle(self, request, data):
        try:
            #change_rack_properties(label=None, rackid=None, new_label=None, data_center=None, location=None, notes=None)
            (rc, result_dict) = device_mgr.change_rack_properties(data['label'], None, None, data['data_center'], data['location'], data['notes'])
            if rc!=0:
               msg = _('Attempt to update rack details for %s failed  Details of the attempt: "%s"' % (data['label'], result_dict))
               messages.error(request, msg)
               logging.error('Unable to edit rack "%s".  Return code "%s" received.  Details of the failure: "%s"' % (data['label'], rc, result_dict))
            else:
               # must have a 0 rc -- display completion msg
               msg = _('Rack details successfully updated.')
               messages.info(request, msg)
            return True           
        except Exception:
            exceptions.handle(request,
                              _('Unable to edit rack details.'))

    def __init__(self, *args, **kwargs):
        super(EditRack, self).__init__(*args, **kwargs) 
