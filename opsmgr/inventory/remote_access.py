import logging
import select
import socket
import sys
import termios
import tty

from paramiko import AutoAddPolicy
from paramiko import SSHClient
from paramiko.py3compat import u

import opsmgr.inventory.persistent_mgr as persistent_mgr

def remote_access(label):
    """Establish ssh shell access to remote endpoint

    Args:
        label:  label of the device to establish shell with

    Returns:
        rc: return code
        message: message associated with return code returned
    """
    _method_ = 'device_mgr.remote_access'
    device = persistent_mgr.get_device_by_label(label)
    if device:
        address = device.address
        userid = device.userid
        password = persistent_mgr.decrypt_data(device.password)
        logging.info(
            "%s::Retrieved device details. Opening remote shell to the device (%s).",
            _method_, label)
        try:
            print(_(
                "Establishing remote SSH connection to device (%s).") % label)
            _create_remote_connection(
                label, address, userid, password)
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
    return 0, message

def _create_remote_connection(remote_access_label, address, userid, password):
    """ create a remote ssh connection based on the information provided.

    Args:
        remote_access_label: label of device we are connecting to.
        address: IPv4 address of device to connect to
        userid:  userid to authenticate with
        password: password to authenticate with
    """
    _method_ = 'device_mgr._create_remote_connection'
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(
        address, username=userid, password=password, look_for_keys=False)
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
