import frappe

@frappe.whitelist(methods=["GET"])
def get_process(start_date: str):
    """
    Versão recriada da função
    """
    contracts = frappe.db.get_all(
        "Contract",
        fields=["name"],
        filters=[
            ["datainiciomedicao", "<=", start_date],
            ["contratoencerrado", "is", "not set"]
        ]
    )
    
    return {
        "contracts": contracts,
        "total": len(contracts),
        "start_date": start_date
    }