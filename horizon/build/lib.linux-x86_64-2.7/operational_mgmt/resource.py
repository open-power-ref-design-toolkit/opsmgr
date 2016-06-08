class Resource(object):
    # The class "constructor" - It's actually an initializer
    def __init__(self, device):
        self.id = device['deviceid']
        self.name = device['label']
        self.type = device['device-type']
        self.arch = device['architecture']
        self.rack_loc = device['rack-eia-location']
        self.userid = device['userid']
        self.mtm = device['machine-type-model']
        self.serial_num = device['serial-number']
        self.ip_address = device['ip-address']
        self.hostname = device['hostname']
        self.version = device['version']
        self.web_url = device['web_url']
        self.device_id = device['deviceid']

        # displayable host / ip address info
        self.host_name = []
        if (self.hostname is not None) and (self.ip_address is not None):
            # both pieces of info are set.
            self.host_name.append(self.hostname)
            self.host_name.append("(" + self.ip_address + ")")
        elif self.ip_address is not None:
            # only ip address field is set
            self.host_name.append(self.ip_address)
            self.host_name.append("(" + self.ip_address + ")")
        else:
            # only hostname is set
            self.host_name.append(self.hostname)

        # Capabilities
        self.capabilities = []
        for capability in device['capabilities']:
            self.capabilities.append(capability)
