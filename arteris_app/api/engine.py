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

@frappe.whitelist(methods=["GET"])
def get_keys():
    """
    Get all keys from a doctype
    """
    
    body = frappe.form_dict

    doctype = frappe.form_dict.doctype
    filters = frappe.form_dict.filters
    return_field = frappe.form_dict.return_field

    # Get all keys from the doctype
    keys = frappe.db.get_all(doctype, fields=return_field, filters=filters) 
    
    # if not keys:
    #     return {"keys": None}
    
    return keys