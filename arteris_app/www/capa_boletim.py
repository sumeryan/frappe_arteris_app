import frappe
from frappe import _

def get_context(context):
    context.no_cache = 1
    context.show_sidebar = True
    doc_id = frappe.form_dict.get('id')
    if doc_id:
        try:
            context.doc = frappe.get_doc('Contract Measurement', doc_id)
        except frappe.DoesNotExistError:
            frappe.throw(_("Contract Measurement not found"), frappe.DoesNotExistError)
    else:
        frappe.throw(_("No id provided in URL"), frappe.DoesNotExistError)
    return context