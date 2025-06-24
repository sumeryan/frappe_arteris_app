import frappe
from frappe import _
import json

def get_context(context):
    context.no_cache = 1
    context.show_sidebar = True
    doc_id = frappe.form_dict.get('id')
    if doc_id:
        try:
            doc = frappe.get_doc('Contract Measurement', doc_id)
            context.contract_measurement_json = frappe.as_json(doc.as_dict())

            contract = frappe.get_doc('Contract', doc.contrato)
            context.contract_json = frappe.as_json(contract.as_dict())

            concessionaria = frappe.get_doc('Subsidiary', contract.subsidiaria)
            context.concessionaria_json = frappe.as_json(concessionaria.as_dict())

            contractedCompany = frappe.get_doc('Contracted Company', doc.contratada)
            context.contracted_company_json = frappe.as_json(contractedCompany.as_dict())

        except frappe.DoesNotExistError:
            frappe.throw(_("Contract Measurement not found"), frappe.DoesNotExistError)
    else:
        frappe.throw(_("No id provided in URL"), frappe.DoesNotExistError)
    return context