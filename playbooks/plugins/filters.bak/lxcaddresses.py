
def lxcaddress(lxc_addrs, hostvars):
    if lxc_addrs not in globals():
        lxc_addrs = []
    lxc_addrs.append(hostvars.address)
    return lxc_addrs

class FilterModule(object):
    def filters(self):
        return {
            'lxcaddress': lxcaddress,
        }

