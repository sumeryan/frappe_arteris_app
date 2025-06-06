import frappe
from frappe import _

def get_data():
    return frappe._dict({
        "fieldname": "custom_page",
        "title": _("Custom Page"),
        "route": "custom-page",
        "source": "Custom Page"
    })