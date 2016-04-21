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
from django.forms import ValidationError  # noqa

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import validators

import opsmgr.inventory.device_mgr as device_mgr
from openstack_dashboard.dashboards.operational_mgmt.inventory \
    import tabs as inventoryRacks_tabs
import collections
import logging
import pdb

AUTH_METHOD_USER_PWD = u'0'
AUTH_METHOD_USER_KEY = u'1'

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

class PasswordMixin(forms.SelfHandlingForm):
    password = forms.RegexField(
        label=_("Password"),
        widget=forms.PasswordInput(render_value=False),
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()})
    confirm_password = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(render_value=False))
    no_autocomplete = True

    def clean(self):
        '''Check to make sure password fields match.'''
        data = super(forms.Form, self).clean()
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise ValidationError(_('Passwords do not match.'))
        return data

class AddResourceForm(forms.SelfHandlingForm):
    label = forms.CharField(label=_("Label"),
                                  max_length=255,
                                  required=True)
    rackid = forms.ChoiceField(label=_("Rack"), 
                                required = True)   
    eiaLocation = forms.CharField(label=_("EIA Location"),
                                  max_length=3,
                                  required=False)
    ip_address = forms.CharField(label=_("Host Name or IP Address"),
                                  help_text=_("Specify the fully qualified host name or IP V4 address to be used by Operational Management "
                                            "to access the device."),
                                  max_length=255,
                                  required=True)

    authMethod = forms.ChoiceField(label=_('Authentication Method'),
                                     help_text=_("Indicates the type of credential information to be used by Operational Management "
                                               "to access the device."),
                                     choices=[(AUTH_METHOD_USER_PWD, _('User ID and Password')),
                                              (AUTH_METHOD_USER_KEY, _('User ID and SSH Key'))],
                                     widget=forms.Select
                                     (attrs={'class': 'switchable',
                                             'data-slug': 'auth'}))

    # If no initial value is provided on user ID, Chrome wants to prime with a saved userid
    # and prime the password, too -- so give it a space...
    userID = forms.CharField(label=_("User ID"),
                                  initial=_(""),
                                  max_length=255,
                                  required=True)

    password = forms.CharField(label = _("password"), required=True,
                                     widget=forms.PasswordInput
                                     (attrs={'class': 'switched',
                                             'data-switch-on': 'auth',
                                             'data-auth-0': _("Password")},
                                             render_value=False))

    sshKey = forms.CharField(widget=forms.widgets.Textarea(
                                  attrs={'class': 'switched',
                                  'data-switch-on': 'auth',
                                  'data-auth-1': _("SSH Key"),
                                  'rows': 4}),
                                  help_text=_("Paste the private SSH key for the specified device."),
                                  required=True)

    passphrase = forms.CharField(label = _("passphrase"), required=False,
                                     widget=forms.PasswordInput
                                     (attrs={'class': 'switched',
                                             'data-switch-on': 'auth',
                                             'data-auth-1': _("Passphrase")},
                                             render_value=False))


    def __init__(self, request, *args, **kwargs):
        super(AddResourceForm, self).__init__(request, *args, **kwargs) 
        self.fields['rackid'].choices = create_rack_choices()
 
    def clean(self):
        cleaned_data = super(AddResourceForm, self).clean()
        self._clean_auth_ids(cleaned_data)
        return cleaned_data

    def _clean_auth_ids(self, data):
        authMethod = data.get('authMethod')
        
        # if User ID + SSH Key was chosen, we can ignore any 'password' errors
        if (authMethod == AUTH_METHOD_USER_KEY) and ('password' in self._errors):
           del self._errors['password']
        # if User ID + Password was chosen, we can ignore any 'sshKey' errors
        if (authMethod == AUTH_METHOD_USER_PWD) and ('sshKey' in self._errors):
           del self._errors['sshKey']

    def handle(self, request, data):
        try: 
            # Need to ensure we pass along the correct password, and that we don't accidently pass
            # the SSH key
            passwordValue = None
            if data['authMethod'] != AUTH_METHOD_USER_KEY:
               data['sshKey'] = None
               if data.has_key('password'):
                  passwordValue = data['password']   
            else:
               if data.has_key('passphrase'):
                  passwordValue = data['passphrase']
            (rc, result_dict) = device_mgr.add_device(data['label'], None, data['ip_address'], data['userID'].strip(), passwordValue, data['rackid'], data['eiaLocation'], data['sshKey'])

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
    ip_address = forms.CharField(label=_("Host Name or IP Address"),
                                  help_text=_("Specify the fully qualified host name or IP V4 address to be used by Operational Management "
                                            "to access the device."),
                                  max_length=255,
                                  required=True)
    authMethod = forms.ChoiceField(label=_('Authentication Method'),
                                    help_text=_("Indicates the type of credential information to be used by Operational Management "
                                               "to access the device."),
                                     choices=[(AUTH_METHOD_USER_PWD, _('User ID and Password')),
                                              (AUTH_METHOD_USER_KEY, _('User ID and SSH Key'))],
                                     widget=forms.Select
                                     (attrs={'class': 'switchable',
                                             'data-slug': 'auth'}))

    # If no initial value is provided on user ID, Chrome wants to prime with a saved userid
    # and prime the password, too -- so give it a space...
    userID = forms.CharField(label=_("User ID"),
                                  max_length=255,
                                  required=True)

    password = forms.CharField(label = _("password"),
                                     widget=forms.PasswordInput
                                     (attrs={'class': 'switched',
                                             'data-switch-on': 'auth',
                                             'data-auth-0': _("Password")},
                                             render_value=False))

    sshKey = forms.CharField(widget=forms.widgets.Textarea(
                                  attrs={'class': 'switched',
                                  'data-switch-on': 'auth',
                                  'data-auth-1': _("SSH Key"),
                                  'rows': 4}),
                                  help_text=_("Paste the private SSH key for the specified device."))

    passphrase = forms.CharField(label = _("passphrase"),
                                     widget=forms.PasswordInput
                                     (attrs={'class': 'switched',
                                             'data-switch-on': 'auth',
                                             'data-auth-1': _("Passphrase")},
                                             render_value=False), required=False)
    def __init__(self, request, *args, **kwargs):
        super(EditResourceForm, self).__init__(request, *args, **kwargs)       
        self.fields['rackid'].choices = create_rack_choices()

    def clean(self):
        cleaned_data = super(EditResourceForm, self).clean()
        self._clean_auth_ids(cleaned_data)
        return cleaned_data

    def _clean_auth_ids(self, data):
        authMethod = data.get('authMethod')
        old_authMethod = self.initial['authMethod']
        authMethodChanged = int(authMethod) != old_authMethod

        # if we have an sshKey value (but it's empty), or we don't have an sshKey value at all 
        if ((data.has_key('sshKey') and data['sshKey'] == u'') or (data.has_key('sshKey') == False)):
           # and if the auth method has changed to user/key
           if (authMethodChanged and (authMethod == AUTH_METHOD_USER_KEY)):
              # we really do have an error 
              self._errors['sshKey'] = ["Because you are changing the authentication method for this device to 'User ID and SSH Key', you must supply an SSH Key value."]
           # else if the auth method is user/key, and the user id value has changed from its initial value
           elif ((authMethod == AUTH_METHOD_USER_KEY) and (self.initial['userID'] != data['userID'])):
              # we really do have an error
              self._errors['sshKey'] = ["Because you are using the authentication method 'User ID and SSH Key' for this device and are changing the User ID, you must supply an SSH Key value."]
           # else we don't have an sshKey (and) we don't need an ssh key -- no error
           else: del self._errors['sshKey']
        else:
           # we have an ssh key -- no error needed
           if (self._errors.has_key('sshKey')):
              del self._errors['sshKey']

        # if we have a password value (but it's empty), or we don't have a password value at all
        if ((data.has_key('password') and data['password'] == u'') or (data.has_key('password') == False)):
           # and if the auth method has changed to user/password
           if (authMethodChanged and (authMethod == AUTH_METHOD_USER_PWD)):	
              # we really do have an error
              self._errors['password'] = ["Because you are changing the authentication method for this device to 'User ID and Password', you must supply a password value."]
           # else if the auth method is user/password, and the user id value has changed from its initial value
           elif ((authMethod == AUTH_METHOD_USER_PWD) and (self.initial['userID'] != data['userID'])):
              # we really do have an error
              self._errors['password'] = ["Because you are using the authentication method 'User ID and Password' for this device and are changing the User ID, you must supply a password value."]
           # else we don't have a password (and) we don't need a password -- no error
           else: del self._errors['password']
        else:
           # we have have a password -- no error needed
           if (self._errors.has_key('password')):
              del self._errors['password']

    def handle(self, request, data):
        try: 

            # Determine what fields have changed
            newLabel = None
            if data.has_key('label') and self.initial['label'] != data['label']:
               newLabel = data['label']
            newUserID = None
            if data.has_key('userID') and  self.initial['userID'] != data['userID']:
               newUserID = data['userID']
            newPassword = None
            if data.has_key('password') and data['password'] != None:
               newPassword = data['password']
            newIPAddress = None
            if data.has_key('ip_address') and self.initial['ip_address'] != data['ip_address']:
               newIPAddress = data['ip_address']
            newRackid = None
            if data.has_key('rackid') and self.initial['rackid'] != int(data['rackid']):
               newRackid = data['rackid']
            newEIALocation = None
            if data.has_key('eiaLocation') and self.initial['eiaLocation'] != data['eiaLocation']:
               newEIALocation = data['eiaLocation']
            newSSHKey = None
            if data.has_key('sshKey') and data['sshKey'] != None:
               newSSHKey = data['sshKey']
               if data.has_key('passphrase') and data['passphrase'] != None:
                  newPassword = data['passphrase']


            # Need to ensure we don't inadvertantly pass an ssh key to the edit_device api...
            if data['authMethod'] != AUTH_METHOD_USER_KEY:
               data['sshKey'] = None

            #def change_device_properties(label=None, deviceid=None, new_label=None,
            #                 userid=None, password=None, address=None,
            #                 rackid=None, rack_location=None, ssh_key=None):
            (rc, result_dict) = device_mgr.change_device_properties(None, self.initial['deviceId'], newLabel, newUserID, newPassword, newIPAddress, newRackid, newEIALocation, newSSHKey)
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

class ChangePasswordForm(PasswordMixin, forms.SelfHandlingForm):
    userID = forms.CharField(label=_("User ID"),
                                  max_length=255, required=False)
    label = forms.CharField(label=_("Resource Label"),
                                  max_length=255, required=False)

    oldpassword = forms.CharField(label = _("Original Password"), required=True,
                                     widget=forms.PasswordInput
                                     (render_value=False))
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        # Reorder form fields from multiple inheritance
        ordering = ["userID", "label",
                    "oldpassword", "password",
                    "confirm_password"]
        self.fields = collections.OrderedDict(
            (key, self.fields[key]) for key in ordering)
        readonlyInput = forms.TextInput(attrs={'readonly': 'readonly'})
        self.fields["label"].widget = readonlyInput
        self.fields["userID"].widget = readonlyInput

    def handle(self, request, data):
        try:      
            #change_device_password(label=None, deviceid=None, old_password=None, new_password=None)      
            (rc, result_dict) = device_mgr.change_device_password(data['label'], None, data['oldpassword'], data['password'])
            if rc!=0:
               # failure case -- so use the initial label for logging/message
               msg = _('Attempt to change the password for user "%s" on resource "%s" was not successful. Details of the attempt: "%s"' % (data['userID'], data['label'], result_dict))
               messages.error(request, msg)
               logging.error('Unable to change password for user "%s" on resource "%s".  Return code "%s" received.  Details of the failure: "%s"' % (data['userID'], data['label'], rc, result_dict))
            else:
               # must have a 0 rc -- display completion msg -- use current label for message
               msg = _('Password changed successfully for user "%s" on resource "%s".' % (data['userID'], data['label']))
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
