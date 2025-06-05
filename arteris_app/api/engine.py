import frappe

@frappe.whitelist(methods=["POST"])
def update_doctype():
    """
    Update doctype from engine
    """

    body = frappe.form_dict
    
    engine_doctype = frappe.form_dict.doctype
    engine_field = frappe.form_dict.field
    engine_name = frappe.form_dict.id
    engine_value = frappe.form_dict.value

    # Get all contract items from the database
    set_result = frappe.db.set_value(engine_doctype, engine_name, engine_field, engine_value)
    return set_result