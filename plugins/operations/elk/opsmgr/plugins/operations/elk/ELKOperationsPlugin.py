import os

from backports import configparser
from opsmgr.inventory.interfaces.IOperationsPlugin import IOperationsPlugin
from opsmgr.inventory import plugins
from opsmgr.common.utils import entry_exit

class ELKPlugin(IOperationsPlugin):

    OPSMGR_CONF = "/etc/opsmgr/opsmgr.conf"
    ELK_SECTION = "ELK"

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def get_application_url():
        if os.path.exists(ELKPlugin.OPSMGR_CONF):
            parser = configparser.ConfigParser()
            parser.read(ELKPlugin.OPSMGR_CONF, encoding='utf-8')
            web_protcol = parser.get(ELKPlugin.ELK_SECTION, "web_protocol")
            web_proxy = parser.get(ELKPlugin.ELK_SECTION, "web_proxy")
            web_port = parser.get(ELKPlugin.ELK_SECTION, "web_port")
            application = "ELK"
            capability = "logging"
            return plugins.PluginApplication(application, capability, web_protcol, web_proxy,
                                             web_port, None)
        else:
            return None
