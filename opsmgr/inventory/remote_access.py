import logging
import select
import socket
import sys
import termios
import tty

try:
    #python 2.7
    from StringIO import StringIO
except ImportError:
    #python 3.4
    from io import StringIO

import paramiko
from paramiko.py3compat import u

from opsmgr.inventory import persistent_mgr
from opsmgr.common.utils import entry_exit

@entry_exit(exclude_index=[], exclude_name=[])
def remote_access(label):
    """Establish ssh shell access to remote endpoint

    Args:
        label:  label of the device to establish shell with

    Returns:
        rc: return code
        message: message associated with return code returned
    """
    _method_ = 'remote_access.remote_access'
    session = persistent_mgr.create_database_session()
    device = persistent_mgr.get_device_by_label(session, label)
    if device:
        address = device.address
        userid = device.userid
        password = None
        if device.password:
            password = persistent_mgr.decrypt_data(device.password)
        ssh_key_string = None
        key = device.key
        if key:
            ssh_key_string = StringIO(key.value)
            if key.password:
                password = persistent_mgr.decrypt_data(key.password)
        logging.info(
            "%s::Retrieved device details. Opening remote shell to the device (%s).",
            _method_, label)
        try:
            print(_(
                "Establishing remote SSH connection to device (%s).") % label)
            _create_remote_connection(label, address, userid, password, ssh_key_string)
        except Exception as e:
            message = _("Remote access to device (%s) failed due to error :%s") % (
                label, e)
            logging.warning(
                "%s::Failed to connect to device (%s) failed due to error :%s", _method_, label, e)
            return 1, message
    else:
        message = _(
            "Device (%s) not found.") % label
        logging.warning(
            "%s::Device (%s) not found.", _method_, label)
        return 1, message
    logging.info(
        "%s::Remote access to device (%s) successful", _method_, label)
    message = _("Remote access to device (%s) successful") % label
    session.close()
    return 0, message

@entry_exit(exclude_index=[3, 4], exclude_name=["password", "ssh_key_string"])
def _create_remote_connection(remote_access_label, address, userid, password, ssh_key_string):
    """ create a remote ssh connection based on the information provided.

    Args:
        remote_access_label: label of device we are connecting to.
        address: IPv4 address of device to connect to
        userid:  userid to authenticate with
        password: password of userid or ssh_key_string
        ssh_key_string: String containing an ssh private key
    """
    _method_ = 'remote_access._create_remote_connection'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if ssh_key_string:
        private_key = paramiko.RSAKey.from_private_key(ssh_key_string, password)
        ssh.connect(address, username=userid, pkey=private_key, look_for_keys=False)
    else:
        ssh.connect(address, username=userid, password=password, look_for_keys=False)
    chan = ssh.invoke_shell()
    print(_("Remote connection to device (%s) established successfully.") %
          remote_access_label)
    logging.info("%s::Remote connection to device (%s) established successfully.",
                 _method_, remote_access_label)
    _open_interactive_shell(chan)
    print(_("Remote connection to device (%s) disconnected.") %
          remote_access_label)
    logging.info("%s::Remote connection to device (%s) disconnected.",
                 _method_, remote_access_label)

@entry_exit(exclude_index=[], exclude_name=[])
def _open_interactive_shell(chan):
    '''    Opens a remote terminal interface
    Note: Works only on unix as it uses POSIX style tty control
    '''

    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)

        while True:
            r, dummy_w, dummy_e = select.select([chan, sys.stdin], [], [])
            if chan in r:
                try:
                    x = u(chan.recv(1024))
                    if len(x) == 0:
                        sys.stdout.write(
                            '\r\n*** Terminating the remote shell.\r\n')
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:
                x = sys.stdin.read(1)
                if len(x) == 0:
                    break
                chan.send(x)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
