
def lxcaddress(lxc_info, lxc_name):
    for i, res in enumerate(lxc_info['results']):
        if res['item']['name'] == lxc_name:
            return res['lxc_container']['ips'][0]
    return None

class FilterModule(object):
    def filters(self):
        return {
            'lxcaddress': lxcaddress,
        }

