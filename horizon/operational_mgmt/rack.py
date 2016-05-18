class Rack(object):
    # The class "constructor" - It's actually an initializer
    def __init__(self, device):
        self.id = device['rackid']
        self.name = device['label']
        self.data_center = device['data-center']
        self.rack_loc = device['location']
        self.notes = device['notes']
