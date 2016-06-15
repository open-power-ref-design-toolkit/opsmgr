import os

CREDS_DIR = "/usr/local/nagios/opsmgr/nagios_config/.creds"


def retrieveAccessInfoForDevice(address):
    userid = None
    password = None
    ssh_key = None
    if os.path.exists(CREDS_DIR):
        file = CREDS_DIR + "/." + address + ".creds"
        with open(file, 'r') as input:
            userid = input.readline().strip()
            password = input.readline().strip()
            ssh_key = input.read().strip()
            if password == "":
                password = None
            if ssh_key =="":
                ssh_key = None
    return (userid, password, ssh_key)
