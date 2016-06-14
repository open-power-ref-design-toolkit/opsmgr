import logging
from opsmgr.common.utils import entry_exit, load_plugin_by_namespace

I_DISCOVERY_PLUGIN = "opsmgr.discovery.interfaces.IDiscoveryPlugin"

@entry_exit(exclude_index=[], exclude_name=[])
def _load_plugins():
    """ Find the discovery provider plugins and return them as
        dictonary[name]=plugin class
    """
    return load_plugin_by_namespace(I_DISCOVERY_PLUGIN)

@entry_exit(exclude_index=[], exclude_name=[])
def list_plugins():
    return sorted(_load_plugins().keys())

@entry_exit(exclude_index=[], exclude_name=[])
def find_resources():
    plugins = _load_plugins()
    plugin_label = 'unknown' #keeps pylint happy
    message = None
    try:
        for plugin_label, plugin in plugins.items():
            plugin.find_resources()
    except Exception as e:
        logging.exception(e)
        message = _("Error in plugin (%s)::Unable to find resources - reason::%s") % \
                  (plugin_label, e)
        return -1, message
    return 0, message

@entry_exit(exclude_index=[], exclude_name=[])
def import_resources(resource_label='*', offline=False):
    plugins = _load_plugins()
    plugin_label = 'unknown' #keeps pylint happy
    message = None
    try:
        for plugin_label, plugin in plugins.items():
            plugin.import_resources(resource_label, offline)
    except Exception as e:
        logging.exception(e)
        message = _("Error in plugin (%s)::Unable to import resource - reason::%s") % \
                 (plugin_label, e)
        return -1, message
    return 0, message
