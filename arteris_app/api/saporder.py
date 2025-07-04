import frappe

@frappe.whitelist(methods=["POST"])
def copylines():

    lines = frappe.db.get_all("SAP Order Period", fields=["name","parent","linhapedido"])

    for l in lines:
        check = frappe.db.get_all("SAP Order Period Link", fields=["name"], filters={"name": l['name']})
        if not check:
            doc_link = frappe.new_doc('SAP Order Period Link')
            doc_link.name = l['name']
            doc_link.linha = f"{l['parent']}-{l['linhapedido']}"
            doc_link.pedidosap = l['parent']
            doc_link.save()

    return {"Processed": True}