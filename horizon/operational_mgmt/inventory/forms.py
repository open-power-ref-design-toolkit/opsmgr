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

import collections
from django.forms import ValidationError  # noqa
from django.utils.translation import ugettext_lazy as _


from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import validators

import logging
import opsmgr.inventory.rack_mgr as rack_mgr
import opsmgr.inventory.resource_mgr as resource_mgr

AUTH_METHOD_USER_PWD = u'0'
AUTH_METHOD_USER_KEY = u'1'


def create_rack_choices(request):
    __method__ = 'forms.create_rack_choices'
    rack_choices = []
    (rc, result_dict) = rack_mgr.list_racks()
    if rc is not 0:
        # Non-zero RC -- unexpected
        messages.error(
            request, _(
                'Unable to retrieve Operational'
                ' Management inventory information for rack extensions.'))
        logging.error(
            "%s: Unable to retrieve Operational Management rack"
            " inventory information. A Non-0 return code returned from"
            " rack_mgr.list_racks.  The return code is: %s.  Details"
            " of the attempt: %s", __method__, rc, result_dict)
    else:
        value = result_dict['racks']
        for s in value:
            rack_choices.append((s['rackid'], s['label']))
    return rack_choices


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
        data = super(PasswordMixin, self).clean()
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise ValidationError(_('Passwords do not match.'))
        return data


class AddResourceForm(forms.SelfHandlingForm):
    label = forms.CharField(label=_("Label"), max_length=255,
                            required=True)
    rackid = forms.CharField(label=_("Rack ID"), widget=forms.HiddenInput())
    rack_label = forms.CharField(label=_("Rack"), max_length=255,
                                 required=True)
    eiaLocation = forms.CharField(
        label=_("EIA Location"),
        max_length=3, required=False)
    ip_address = forms.CharField(
        label=_("Host Name or IP Address"),
        max_length=255, required=True,
        help_text=_("Specify the fully qualified host name or IP V4 address "
                    "used by Operational Management to access the "
                    " resource."))
    auth_method = forms.ChoiceField(
        label=_('Authentication Method'),
        choices=[(AUTH_METHOD_USER_PWD, _('User ID and Password')),
                 (AUTH_METHOD_USER_KEY, _('User ID and SSH Key'))],
        widget=forms.Select(attrs={'class': 'switchable', 'data-slug':
                                   'auth'}),
        help_text=_("Indicates the type of credential information "
                    "used by Operational Management to access the resource."))
    userID = forms.CharField(label=_("User ID"),
                             max_length=255, required=True)
    password = forms.CharField(
        label=_("password"), required=True,
        widget=forms.PasswordInput(
            attrs={'class': 'switched',
                   'data-switch-on': 'auth', 'data-auth-0': _("Password")},
            render_value=False))
    sshKey = forms.CharField(
        widget=forms.widgets.Textarea(
            attrs={'class': 'switched', 'data-switch-on': 'auth',
                   'data-auth-1': _("SSH Key"), 'rows': 4}),
        required=True,
        help_text=_("Paste the private SSH key for the specified"
                    " resource."))
    passphrase = forms.CharField(
        label=_("passphrase"), required=False,
        widget=forms.PasswordInput(attrs={'class': 'switched',
                                          'data-switch-on': 'auth',
                                          'data-auth-1': _("Passphrase")},
                                   render_value=False))

    def __init__(self, request, *args, **kwargs):
        super(AddResourceForm, self).__init__(request, *args, **kwargs)
        # User should only be allowed to add to the rack being displayed
        self.fields["rack_label"].widget = forms.TextInput(
            attrs={'readonly': 'readonly'})

    def clean(self):
        cleaned_data = super(AddResourceForm, self).clean()
        self._clean_auth_ids(cleaned_data)
        return cleaned_data

    def _clean_auth_ids(self, data):
        auth_method = data.get('auth_method')

        # if User ID + SSH Key was chosen, we can ignore any 'password' errors
        if (auth_method == AUTH_METHOD_USER_KEY) and ('password' in
                                                      self._errors):
            del self._errors['password']
        # if User ID + Password was chosen, we can ignore any 'sshKey' errors
        if (auth_method == AUTH_METHOD_USER_PWD) and ('sshKey' in
                                                      self._errors):
            del self._errors['sshKey']

    def handle(self, request, data):
        __method__ = 'forms.AddResourceForm.handle'
        try:
            # Need to ensure we pass along the correct password (either
            # password or phassphrase), and that we don't accidently pass
            # the SSH key
            password_value = None
            if data['auth_method'] != AUTH_METHOD_USER_KEY:
                data['sshKey'] = None
                if 'password' in data:
                    password_value = data['password']
            else:
                if 'passphrase' in data:
                    password_value = data['passphrase']

            logging.debug("%s: Attempting to add a resource to rack: %s, using"
                          " label: %s, address: %s, user id: %s, eia location"
                          " %s, and authentication method: %s", __method__,
                          self.initial['rackid'], data['label'],
                          data['ip_address'], data['userID'],
                          data['eiaLocation'], data['auth_method'])

            # pass in "None" for resource type in add_resource -- so that the
            # API will determine type for us
            (rc, result_dict) = resource_mgr.add_resource(
                data['label'], None, data['ip_address'],
                data['userID'].strip(), password_value,
                self.initial['rackid'], data['eiaLocation'], data['sshKey'])

            if rc is not 0:
                # Log details of the unsuccessful attempt.
                logging.error("%s: Attempt to add a resource to rack: %s, "
                              "using label: %s, address: %s, user id: %s, "
                              "eia location %s, and authentication method:"
                              " %s failed.", __method__,
                              self.initial['rackid'], data['label'],
                              data['ip_address'], data['userID'],
                              data['eiaLocation'], data['auth_method'])

                logging.error(
                    "%s: Unable to add resource %s to rack %s. A Non-0 "
                    " return code returned from resource_mgr.add_resource."
                    " The return code is: %s. Details of the attempt: "
                    " %s", __method__, data['label'], self.initial['rackid'],
                    rc, result_dict)
                msg = str(
                    'Attempt to add resource ' + data['label'] + ' was ' +
                    'not successful. Details of the attempt: ' + result_dict)
                messages.error(request, msg)
                # Return false in this case so that the dialog is not
                # dismissed.  This gives the end-user a chance to
                # update the dialog w/o having to re-enter all the
                # information a second time.
                return False
            else:
                msg = str('Resource ' + data['label'] + ' successfully' +
                          ' added.')
                messages.success(request, msg)
                return True
        except Exception as e:
            logging.error("%s: Exception received trying to add a resource.  "
                          "Exception is: %s", __method__, e)
            exceptions.handle(request,
                              _('Unable to add resource.'))
            # In this case, return True so that the dialog closes.
            # In theory, there are no values the end-user could change
            # to the dialog inputs that would allow us to proceed.
            return True


class EditResourceForm(forms.SelfHandlingForm):
    label = forms.CharField(
        label=_("Label"),
        max_length=255, required=True)
    rackid = forms.ChoiceField(
        label=_("Rack"),
        required=True)
    eiaLocation = forms.CharField(
        label=_("EIA Location"),
        max_length=3, required=False)
    ip_address = forms.CharField(
        label=_("Host Name or IP Address"),
        max_length=255, required=True,
        help_text=_(
            "Specify the fully qualified host name or IP V4"
            " address used by Operational Management to access"
            " the resource."))
    auth_method = forms.ChoiceField(
        label=_('Authentication Method'),
        choices=[(AUTH_METHOD_USER_PWD, _('User ID and Password')),
                 (AUTH_METHOD_USER_KEY, _('User ID and SSH Key'))],
        widget=forms.Select(attrs={'class': 'switchable',
                                   'data-slug': 'auth'}),
        help_text=_("Indicates the type of credential information used "
                    "by Operational Management to access the resource."))
    userID = forms.CharField(label=_("User ID"), max_length=255,
                             required=True)
    password = forms.CharField(
        label=_("password"),
        widget=forms.PasswordInput(attrs={'class': 'switched',
                                          'data-switch-on': 'auth',
                                          'data-auth-0': _("Password")},
                                   render_value=False),
        help_text=_(
            "This is the password that Operational Management should"
            " use when accessing the resource.  Specifying a value here does"
            " not change the password of the user on the resource."))
    sshKey = forms.CharField(
        widget=forms.widgets.Textarea(
            attrs={'class': 'switched', 'data-switch-on': 'auth',
                   'data-auth-1': _("SSH Key"), 'rows': 4}),
        help_text=_("Paste the private SSH key for the specified resource."))
    passphrase = forms.CharField(
        label=_("passphrase"),
        widget=forms.PasswordInput(attrs={'class': 'switched',
                                          'data-switch-on': 'auth',
                                          'data-auth-1': _("Passphrase")},
                                   render_value=False),
        required=False)

    def __init__(self, request, *args, **kwargs):
        super(EditResourceForm, self).__init__(request, *args, **kwargs)
        self.fields['rackid'].choices = create_rack_choices(request)

    def clean(self):
        cleaned_data = super(EditResourceForm, self).clean()
        self._clean_auth_ids(cleaned_data)
        return cleaned_data

    def _clean_auth_ids(self, data):
        auth_method = data.get('auth_method')
        auth_method_changed = int(auth_method) != self.initial['auth_method']

        # if we have an sshKey value (but it's empty), or we don't
        # have an sshKey value at all
        if (('sshKey' in data and data['sshKey'] == u'') or
                ('sshKey' not in data)):
            # and if the auth method has changed to user/key
            if auth_method_changed and (auth_method == AUTH_METHOD_USER_KEY):
                # we really do have an error
                self._errors['sshKey'] = [
                    "Because you are changing the authentication"
                    " method for this resource to 'User ID and"
                    " SSH Key', you must supply an SSH Key value."]
            # else if the auth method is user/key, and the
            # user id value has changed from its initial value
            elif ((auth_method == AUTH_METHOD_USER_KEY) and
                  (self.initial['userID'] != data['userID'])):
                # we really do have an error
                self._errors['sshKey'] = [
                    "Because you are using the authentication"
                    " method 'User ID and SSH Key' for this "
                    " resource and are changing the User ID,"
                    " you must supply an SSH Key value."]
            # else we don't have an sshKey (and) we don't need an ssh key
            # (no error needed)
            else:
                del self._errors['sshKey']
        else:
            # we have an ssh key -- no error needed
            if 'sshKey' in self._errors:
                del self._errors['sshKey']

        # if we have a password value (but it's empty), or we don't
        # have a password value at all
        if (('password' in data and data['password'] == u'') or
                ('password' not in data)):
            # and if the auth method has changed to user/password
            if auth_method_changed and (auth_method == AUTH_METHOD_USER_PWD):
                # we really do have an error
                self._errors['password'] = [
                    "Because you are changing the authentication"
                    " method for this resource to 'User ID and"
                    " Password', you must supply a password value."]
            # else if the auth method is user/password, and the user id
            # value has changed from its initial value
            elif ((auth_method == AUTH_METHOD_USER_PWD) and
                  (self.initial['userID'] != data['userID'])):
                # we really do have an error
                self._errors['password'] = [
                    "Because you are using the authentication"
                    " method 'User ID and Password' for this"
                    " resource and are changing the User ID,"
                    " you must supply password value."]
            # else we don't have a password (and) we don't need a password
            # (no error needed)
            else:
                del self._errors['password']
        else:
            # we have have a password -- no error needed
            if 'password' in self._errors:
                del self._errors['password']

    def handle(self, request, data):
        __method__ = 'forms.EditResourceForm.handle'
        try:
            # We only want to pass the changed fields to the API.
            # Determine what fields have changed (we will process
            # authentication-related fields after this block)
            new_label = None
            if ('label' in data) and (self.initial['label'] !=
                                      data['label']):
                new_label = data['label']
            new_user_id = None
            if ('userID' in data) and (self.initial['userID'] !=
                                       data['userID']):
                new_user_id = data['userID']
            new_ip_address = None
            if ('ip_address' in data) and (self.initial['ip_address'] !=
                                           data['ip_address']):
                new_ip_address = data['ip_address']
            new_rackid = None
            if ('rackid' in data) and (self.initial['rackid'] !=
                                       int(data['rackid'])):
                new_rackid = data['rackid']
            new_eia_location = None
            if ('eiaLocation' in data) and (self.initial['eiaLocation']
                                            != data['eiaLocation']):
                new_eia_location = data['eiaLocation']

            # Need to ensure we pass correct authentication-related fields
            new_password = None
            new_ssh_key = None
            if data['auth_method'] != AUTH_METHOD_USER_KEY:
                # user id and password authentication
                if 'password' in data and data['password'] is not None:
                    new_password = data['password']
            else:
                # user id and SSH key (and passphrase) authentication
                if 'sshKey' in data and data['sshKey'] is not None:
                    new_ssh_key = data['sshKey']
                    # only specify a passphrase if we are setting the sshKey
                    if 'passphrase' in data and data['passphrase'] is not None:
                        new_password = data['passphrase']
            # pass in "None" for original resource label; also, we will
            # pass in the resource ID so the API knows which resource is
            # being edited
            logging.debug("%s: Attempting to edit resource %s on rack: %s, "
                          "using label: %s, address: %s, user id: %s, eia "
                          "location %s, new rack %s, and authentication "
                          " method: %s", __method__, self.initial['label'],
                          self.initial['rackid'], new_label, new_ip_address,
                          new_user_id, new_eia_location, new_rackid,
                          data['auth_method'])

            (rc, result_dict) = resource_mgr.change_resource_properties(
                None, self.initial['resourceId'], new_label, new_user_id,
                new_password, new_ip_address, new_rackid, new_eia_location,
                new_ssh_key)
            if rc is not 0:
                # Log details of the unsuccessful attempt.
                logging.error("%s: Attempt to edit resource %s on rack: %s,"
                              " using new label: %s, address: %s, user id:"
                              " %s, eia location %s, new rack %s, and"
                              " authentication method: %s failed.", __method__,
                              self.initial['label'], self.initial['rackid'],
                              new_label, new_ip_address, new_user_id,
                              new_eia_location, new_rackid,
                              data['auth_method'])

                logging.error(
                    "%s: Unable to edit resource %s to rack %s.  A Non-0"
                    " return code returned from resource_mgr.edit_resource."
                    " The return code is: %s.  Details of the attempt: "
                    " %s", __method__, self.initial['label'],
                    self.initial['rackid'], rc, result_dict)
                # failure case -- so use the initial label for logging/message
                msg = str('Attempt to edit resource ' +
                          self.initial['label'] + " was not successful." +
                          ' Details of the attempt: ' + result_dict)
                messages.error(request, msg)

                # Return false in this case so that the dialog is not
                # dismissed.  This gives the end-user a chance to
                # update the dialog w/o having to re-enter all the
                # information a second time.
                return False
            else:
                # must have a 0 rc -- display completion msg -- use current
                # label for message
                msg = str('Resource ' + data['label'] +
                          ' successfully edited.')
                messages.success(request, msg)
                return True
        except Exception as e:
            logging.error("%s: Exception received trying to edit resource."
                          " Exception is: %s", __method__, e)
            exceptions.handle(request, _('Unable to edit selected resource.'))
            # In this case, return True so that the dialog closes.
            # In theory, there are no values the end-user could change
            # to the dialog inputs that would allow us to proceed.
            return True


class ChangePasswordForm(PasswordMixin, forms.SelfHandlingForm):
    userID = forms.CharField(label=_("User ID"),
                             max_length=255, required=False)
    label = forms.CharField(label=_("Resource Label"),
                            max_length=255, required=False)
    oldpassword = forms.CharField(label=_("Original Password"),
                                  required=True, widget=forms.PasswordInput
                                  (render_value=False))

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        # Reorder form fields from multiple inheritance
        ordering = ["userID",
                    "label",
                    "oldpassword",
                    "password",
                    "confirm_password"]
        self.fields = collections.OrderedDict(
            (key, self.fields[key]) for key in ordering)
        read_only_input = forms.TextInput(attrs={'readonly': 'readonly'})
        self.fields["label"].widget = read_only_input
        self.fields["userID"].widget = read_only_input

    def handle(self, request, data):
        __method__ = 'forms.ChangePasswordForm.handle'
        try:
            # pass in "None" for resource label -- we'll instead pass in the
            # resource ID so the API knows which resource to act on
            (rc, result_dict) = resource_mgr.change_resource_password(
                None, self.initial['resourceid'], data['oldpassword'],
                data['password'])
            if rc is not 0:
                # failure case -- so use the initial label for logging/message
                msg = str('Attempt to change the password for' +
                          ' user "' + data['userID'] + '" on resource' +
                          ' "' + data['label'] + '" was not successful.' +
                          ' Details of the attempt: ' + result_dict)
                messages.error(request, msg)
                logging.error(
                    '%s: Unable to change password for user "%s" on'
                    ' resource "%s".  Return code "%s" received.  Details'
                    ' of the failure: "%s"', __method__,
                    data['userID'], data['label'], rc, result_dict)

                # Return false in this case so that the dialog is not
                # dismissed.  This gives the end-user a chance to
                # update the dialog w/o having to re-enter all the
                # information a second time.
                return False
            else:
                # must have a 0 rc -- display completion msg -- use
                # current label for message
                msg = str('Password changed successfully for' +
                          ' user ' + data['userID'] + ' on' +
                          ' resource ' + data['label'])
                messages.success(request, msg)
                return True
        except Exception as e:
            logging.error("%s: Exception received trying to change the"
                          " password of the selected resource.  Exception"
                          " is: %s", __method__, e)
            exceptions.handle(request, _('Unable to change password for'
                                         ' the selected resource.'))
            # In this case, return True so that the dialog closes.
            # In theory, there are no values the end-user could change
            # to the dialog inputs that would allow us to proceed.
            return True


class EditRackForm(forms.SelfHandlingForm):
    rack_id = forms.CharField(label=_("Rack ID"), widget=forms.HiddenInput())
    label = forms.CharField(label=_("Label"),
                            max_length=255,
                            required=True)
    data_center = forms.CharField(label=_("Data Center"),
                                  max_length=255,
                                  required=False)
    room = forms.CharField(label=_("Room"),
                           max_length=255,
                           required=False)
    row = forms.CharField(label=_("Row"),
                          max_length=255,
                          required=False)
    notes = forms.CharField(label=_("Notes"),
                            max_length=255,
                            required=False)

    def handle(self, request, data):
        __method__ = 'forms.EditRackForm.handle'
        try:
            # pass in "None" for rack label -- we'll instead pass in the
            # rack ID so the API knows which rack to act on
            logging.debug("%s: Attempting to edit rack %s using"
                          " label: %s, data center: %s, room: %s, row: %s, "
                          " notes: '%s.'", __method__, self.initial['label'],
                          data['label'], data['data_center'],
                          data['room'], data['row'], data['notes'])
            (rc, result_dict) = rack_mgr.change_rack_properties(
                None, data['rack_id'], data['label'], data['data_center'],
                data['room'], data['row'], data['notes'])
            if rc is not 0:
                logging.error("%s: Attempt to edit rack %s using"
                              " label: %s, data center: %s, "
                              " room: %s, row: %s, and "
                              " notes: '%s' was not successful.", __method__,
                              self.initial['label'], data['label'],
                              data['data_center'], data['room'],
                              data['row'], data['notes'])
                logging.error(
                    '%s: Unable to edit rack "%s".  Return '
                    'code "%s" received.  Details of the failure: "%s"',
                    __method__, self.initial['label'], rc, result_dict)
                msg = str('Attempt to update rack details for ' +
                          self.initial['label'] + ' failed. Details of the' +
                          ' attempt: ' + result_dict)
                messages.error(request, msg)

                # Return false in this case so that the dialog is not
                # dismissed.  This gives the end-user a chance to
                # update the dialog w/o having to re-enter all the
                # information a second time.
                return False
            else:
                # must have a 0 rc -- display completion msg
                msg = str('Rack details successfully updated.')
                messages.success(request, msg)
                return True
        except Exception as e:
            logging.error("%s: Exception received trying to edit the "
                          "selected rack.  Exception is: %s", __method__, e)
            exceptions.handle(request,
                              _('Unable to edit rack details.'))
            # In this case, return True so that the dialog closes.
            # In theory, there are no values the end-user could change
            # to the dialog inputs that would allow us to proceed.
            return True


class RemoveRackForm(forms.SelfHandlingForm):
    rack_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    label = forms.CharField(label=_("Rack"), required=False)

    def __init__(self, *args, **kwargs):
        super(RemoveRackForm, self).__init__(*args, **kwargs)
        read_only_input = forms.TextInput(attrs={'readonly': 'readonly'})
        self.fields["label"].widget = read_only_input

    def handle(self, request, data):
        __method__ = 'forms.RemoveRackForm.handle'
        try:
            # pass in "None" for rack label -- we'll instead pass in the
            # rack ID so the API knows which rack to act on.  Also pass in
            # False so the API knows to NOT remove all racks
            (rc, result_dict) = rack_mgr.remove_rack(
                None, False, [int(data['rack_id'])])
            if rc is not 0:
                msg = str(
                    'Attempt to remove rack with label ' +
                    data['label'] + ' was not successful. ' +
                    'Details of the attempt: ' + result_dict)
                messages.error(request, msg)
                logging.error(
                    '%s: Unable to remove rack with label "%s".  Return '
                    'code "%s" received.  Details of the failure: "%s"',
                    __method__, data['label'], rc, result_dict)

                # Return false in this case so that the dialog is not
                # dismissed.  This gives the end-user a chance to
                # update the dialog w/o having to re-enter all the
                # information a second time.
                return False
            else:
                # must have a 0 rc -- display completion msg
                msg = str('Rack successfully removed.')
                messages.success(request, msg)
                return True
        except Exception as e:
            logging.error("%s: Exception received trying to remove the "
                          "selected rack.  Exception is: %s", __method__, e)
            exceptions.handle(request, _('Unable to remove rack.'))
            # In this case, return True so that the dialog closes.
            # In theory, there are no values the end-user could change
            # to the dialog inputs that would allow us to proceed.
            return True
