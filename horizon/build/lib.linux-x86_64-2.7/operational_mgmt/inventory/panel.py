from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.api import keystone


class Inventory(horizon.Panel):
    name = _("Inventory")
    slug = 'inventory'

    def can_access(self, context):
        if keystone.is_multi_domain_enabled() \
                and not keystone.is_domain_admin(context['request']):
            return False
        return super(Inventory, self).can_access(context)

    @staticmethod
    def can_register():
        return keystone.VERSIONS.active >= 3
