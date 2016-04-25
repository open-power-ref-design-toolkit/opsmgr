import logging
from stevedore import extension

I_DISCOVERY_PLUGIN = "opsmgr.discovery.interfaces.IDiscoveryPlugin"

def _load_by_namespace(namespace):
    plugins = {}
    extensions = extension.ExtensionManager(namespace=namespace)
    for ext in extensions:
        plugins[ext.name] = ext.plugin()
    return plugins

def load_plugins():
    """ Find the discovery provider plugins and return them as
        dictonary[name]=plugin class
    """
    return _load_by_namespace(I_DISCOVERY_PLUGIN)

def list_plugins():
    return sorted(load_plugins().keys())

def find_resources():
    plugins = load_plugins()
    plugin_label = 'unknown' #keeps pylint happy
    message = None
    try:
        for plugin_label, plugin in plugins.items():
            plugin.find_resources()
    except Exception as e:
        logging.exception(e)
        message = _("Error in plugin (%s)::Unable to find resources - reason::%s") % (plugin_label, e)
        return -1, message
    return 0, message

def import_resources(resource_label='*', offline=False):
    plugins = load_plugins()
    plugin_label = 'unknown' #keeps pylint happy
    message = None
    try:
        for plugin_label, plugin in plugins.items():
            plugin.import_resources(resource_label, offline)
    except Exception as e:
        logging.exception(e)
        message = _("Error in plugin (%s)::Unable to import resource - reason::%s") % (plugin_label, e)
        return -1, message
    return 0, message
