import frappe
import json

@frappe.whitelist(methods=["POST"])
def populate_workloadcfg(contract: str):
    """
    Populate the Workload Configuration with default values.
    """
    result = []

    # Get contract period
    contract_period = frappe.db.get_all("Contract", fields=["datainicial","datafinal"], filters={"name": contract })
    
    # For each month in the contract period, create a workload configuration
    if not contract_period:
        return {"message": "Contract not found or does not have a valid period."}
    contract_end = contract_period[0].datafinal
    contract_current_date = contract_period[0].datainicial

    # Get contract itens
    contract_items = frappe.get_all("Contract Item", fields=["name"], filters={"contrato": contract, "is_group": 0})

    # Each year and month in the contract period
    while contract_current_date <= contract_end:

        # get month and year from the current date
        contract_month = contract_current_date.month
        contract_year = contract_current_date.year

        # Check workload configuration exists
        existing_workload = frappe.db.exists("Contract Item Workload Cfg", {
            "contrato": contract,
            "mes": contract_month,
            "ano": contract_year
        })
        if existing_workload:
            continue

        # Create workload itens
        workload = frappe.new_doc("Contract Item Workload Cfg")
        workload.contrato = contract
        workload.mes = contract_month
        workload.ano = contract_year

        for item in contract_items:
            workload_item = workload.append("itens")
            workload_item.item = item.name
            workload_item.valor = 0.0

        save_result = workload.save()
        result.append(save_result)

        contract_current_date = frappe.utils.add_to_date(contract_current_date, months=1)        

    # return results        
    return {"workloads":result}

@frappe.whitelist(allow_guest=False)
def insert_contract_item_workload_cfg(contrato, mes, ano, tabitens):
    if isinstance(tabitens, str):
        tabitens = json.loads(tabitens)
    # Check if the document exists
    existing_name = frappe.db.exists("Contract Item Workload Cfg", {
        "contrato": contrato,
        "mes": mes,
        "ano": ano
    })
    if existing_name:
        doc = frappe.get_doc("Contract Item Workload Cfg", existing_name)

        # Update or add items in the child table (use 'tabitens')
        existing_items = {row.item: row for row in doc.tabitens}
        frappe.log_error(str(tabitens), f"DEBUG: tabitens {str(tabitens)}")
        frappe.log_error(str(existing_items), "DEBUG: existing_items")

        for item in tabitens:
            frappe.log_error(str(item), f"DEBUG: item {str(item)}")
            item_code = item.get("item")
            valor = item.get("valor")
            if item_code in existing_items:
                existing_items[item_code].valor = valor
            else:
                new_row = doc.append("tabitens", {})
                new_row.item = item_code
                new_row.valor = valor
        doc.save()
        frappe.db.commit()
        return doc.name
    else:
        doc = frappe.get_doc({
            "doctype": "Contract Item Workload Cfg",
            "contrato": contrato,
            "mes": mes,
            "ano": ano,
            "tabitens": tabitens
        })
        doc.insert()
        frappe.db.commit()
        return doc.name