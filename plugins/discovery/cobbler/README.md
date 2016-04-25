Temporary README - final version will be directed to user consumption

The scenario for OpsMgr discovery will be very simple:
- we'll have "discovery provider" plugins that need to be installed (similarly to device plugins and inventory hooks)
- we'll have 2 apis added to the opsmgr CLI:
list_supported_provider_plugins - returns the registered types for provider plugins that were installed via the procedure above
import_data - iterates over all registered provider plugins and calls the import_data defined from the interface/abclass they inherit (IProviderPlugin)

The first available provider plugin will be the CobblerProviderPlugin.
For sprint 1 its implementation will be very simple. It will query cobbler to list all "system" elements defined in its database. Each of these elements will be a "device" which data we'll import from Cobbler and then call add_device in opsmgr.
The plugins is only reading the ip_address of the device right now and adding it as a "BareMetal" type of device.
For sprint 2 I'll enhance the plugin to read other things such as:
user/pwd or sshkey from Genesis configuration
OS type from Cobbler data - if Ubuntu, the device will be added as type 'Ubuntu' instead, to mean that this node is ready to be configured via OpenStackAnsible
mac_address - if ip_address is not available but mac_address is, and no OS type is available, we'll use type as "BareMetal" to mean that this node can be configured via Cobbler
a BLOB with all the rest of the data imported from Cobbler
