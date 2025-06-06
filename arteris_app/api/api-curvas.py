import frappe
from frappe import _

@frappe.whitelist()
def get_related_documents(doctype, doc_name):
    """
    Busca documentos relacionados ao documento especificado
    """
    related_docs = {}
    
    # Buscar links do DocType
    meta = frappe.get_meta(doctype)
    
    # Buscar campos de link
    for field in meta.fields:
        if field.fieldtype == 'Link' and field.options:
            try:
                # Buscar documentos que referenciam este documento
                linked_docs = frappe.get_all(
                    field.options,
                    filters={field.fieldname: doc_name},
                    fields=['name']
                )
                
                if linked_docs:
                    related_docs[field.options] = linked_docs
                    
            except Exception:
                continue
    
    # Buscar documentos que referenciam este documento em outros DocTypes
    all_doctypes = frappe.get_all('DocType', 
                                 filters={'istable': 0, 'issingle': 0},
                                 fields=['name'])
    
    for dt in all_doctypes:
        try:
            dt_meta = frappe.get_meta(dt.name)
            for field in dt_meta.fields:
                if field.fieldtype == 'Link' and field.options == doctype:
                    linked_docs = frappe.get_all(
                        dt.name,
                        filters={field.fieldname: doc_name},
                        fields=['name']
                    )
                    
                    if linked_docs:
                        if dt.name not in related_docs:
                            related_docs[dt.name] = []
                        related_docs[dt.name].extend(linked_docs)
                        
        except Exception:
            continue
    
    return related_docs