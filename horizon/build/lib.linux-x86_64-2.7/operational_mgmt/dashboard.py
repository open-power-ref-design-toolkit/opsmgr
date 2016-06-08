from django.utils.translation import ugettext_lazy as _

import horizon


class OpMgmtdashboard(horizon.Dashboard):
    name = _("Operational Management")
    slug = "op_mgmt"
    panels = ("inventory",)  # ,"monitoring","logging")
    default_panel = 'inventory'

horizon.register(OpMgmtdashboard)
