
def updatelxc(lxcs, host, lxc_info):
    print lxc_info
    for i, res in enumerate(lxc_info['results']):
        for j, lxc in enumerate(lxcs):
            if ('address' not in lxc) and (res['item']['name'] == lxc['name']):
                lxc.update({'address': res['lxc_container']['ips'][0], 'host': host})
                break
    return lxcs

class FilterModule(object):
    def filters(self):
        return {
            'updatelxc': updatelxc,
        }

