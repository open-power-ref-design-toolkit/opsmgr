try:
    #python 2.7
    from StringIO import StringIO
except ImportError:
    #python 3.4
    from io import StringIO
import paramiko
from opsmgr.inventory.interfaces.IManagerDeviceHook import IManagerDeviceHook
from opsmgr.inventory import persistent_mgr
from opsmgr.inventory.data_model import DeviceRole

class UlyssesDevicePlugin(IManagerDeviceHook):

    ROLE_FILE = "/etc/role"

    @staticmethod
    def add_device_pre_save(device):
        pass

    @staticmethod
    def remove_device_pre_save(device):
        pass

    @staticmethod
    def change_device_pre_save(device, old_device_info):
        pass

    @staticmethod
    def add_device_post_save(device):
        if device.device_type == "Ubuntu":
            address = device.address
            userid = device.userid
            key = device.key
            if key:
                key_string = key.value
                if key.password is not None:
                    password = persistent_mgr.decrypt_data(key.password)
                else:
                    password = None
            else:
                key_string = None
                password = persistent_mgr.decrypt_data(device.password)
            client = UlyssesDevicePlugin._connect(address, userid, password, key_string)
            roles = []
            command = "cat " + UlyssesDevicePlugin.ROLE_FILE
            (_stdin, stdout, _stderr) = client.exec_command(command)
            for line in stdout.read().decode().splitlines():
                roles.append(DeviceRole(device.device_id, line.strip()))
            persistent_mgr.add_device_roles(roles)

    @staticmethod
    def remove_device_post_save(device):
        pass

    @staticmethod
    def change_device_post_save(device, old_device_info):
        pass

    @staticmethod
    def _connect(host, userid, password, ssh_key_string=None):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if ssh_key_string:
            private_key = paramiko.RSAKey.from_private_key(StringIO(ssh_key_string), password)
            client.connect(host, username=userid, pkey=private_key, timeout=30,
                           allow_agent=False)
        else:
            client.connect(host, username=userid, password=password, timeout=30,
                           allow_agent=False)
        return client
