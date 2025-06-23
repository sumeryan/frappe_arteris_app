__version__ = "0.0.1"

import frappe
from arteris_app.utils import filters

frappe.get_jenv().filters.update({
    "formatar_moeda": filters.formatar_moeda,
    "formatar_percentual": filters.formatar_percentual,
    "formatar_data": filters.formatar_data,
})