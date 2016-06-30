
def getaddress(address_pool, used_pool):
    for i, addr in enumerate(address_pool):
        if addr not in used_pool:
            used_pool.append(addr)
            return addr
    return None

class FilterModule(object):
    def filters(self):
        return {
            'getaddress': getaddress,
        }

