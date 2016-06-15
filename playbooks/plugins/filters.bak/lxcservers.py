
def lxcservers(hvs, lxcs):
    print hvs
    print lxcs
    srvs = {}
    for lxc in lxcs:
        for i, hst in enumerate(hvs[lxc]):
            if hst.lxc.role not in srvs:
                srvs[hst.lxc.role] = []
            srvs[hst.lxc.role].append(hst.address)
    return srvs

class FilterModule(object):
    def filters(self):
        return {
            'lxcservers': lxcservers,
        }

