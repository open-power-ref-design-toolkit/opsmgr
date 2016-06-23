
def lxcaddress(lxc_info, lxc_name):
    for i, res in enumerate(lxc_info['results']):
        if res['item']['name'] == lxc_name:
            for ip in res['lxc_container']['ips']:
                if ip != '10.0.3.1':
                    return ip
    return None

class FilterModule(object):
    def filters(self):
        return {
            'lxcaddress': lxcaddress,
        }

