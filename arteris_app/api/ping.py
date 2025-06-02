import frappe

@frappe.whitelist(methods=["GET"])
def play():
    return "pong"