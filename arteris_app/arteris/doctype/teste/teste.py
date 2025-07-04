import frappe
from frappe.model.document import Document

class Teste(Document):
    pass

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_child_data(doctype, txt, searchfield, start, page_len, filters):
    """
    Método para buscar dados do SAP Order Period (Child Table)
    """
    # Substitua 'Parent DocType' pelo nome do DocType pai real
    return frappe.db.sql("""
        SELECT DISTINCT
            child.name,
            child.name as description
        FROM 
            `tabSAP Order Period` child
        WHERE 
            child.name LIKE %(txt)s
        ORDER BY 
            child.name
        LIMIT %(start)s, %(page_len)s
    """, {
        'txt': '%%%s%%' % txt,
        'start': start,
        'page_len': page_len
    })