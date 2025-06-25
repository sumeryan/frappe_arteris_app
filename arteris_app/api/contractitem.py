import frappe

@frappe.whitelist(methods=["POST"])
def create_item_main(contract: str):
    """
    Create main item for contract
    """

    exists_item = frappe.db.exists("Contract Item", {"contrato": contract, "is_group": 1})
    if exists_item:
        return {"message": "Main item already exists for this contract"}

    contract_doc = frappe.db.get_all("Contract", fields=["name","contrato"], filters={"name": contract})
    
    # Make sure we have a contract document
    if not contract_doc:
        frappe.throw("Contract not found")
    
    # Access the first item in the list
    contract_data = contract_doc[0]
    
    contract_item = frappe.new_doc("Contract Item")
    contract_item.is_group = 1
    contract_item.codigo = f"Contrato {contract_data['contrato']}"
    contract_item.descricao = f"Contrato {contract_data['contrato']}"
    contract_item.contrato = contract_data["name"]
    result = contract_item.save()

    return result

@frappe.whitelist(methods=["POST"])
def create_item_main_all_contracts():
    """
    Create main item for all contracts
    """

    contracts = frappe.get_all("Contract", fields=["name"])
    
    for contract in contracts:
        create_item_main(contract.name)
    
    return {"message": "Main items created for all contracts"}

    # contracts = frappe.get_all("Contract", fields=["name"])
    
    # for contract in contracts:

    #     contract_doc = frappe.db.get_all("Contract", fields=["name","contrato"], filters={"name": contract.name})

    #     # Make sure we have a contract document
    #     if not contract_doc:
    #         frappe.throw("Contract not found")

    #     # Access the first item in the list
    #     contract_data = contract_doc[0]

    #     contract_item = frappe.new_doc("Contract Item")
    #     contract_item.old_parent = None
    #     contract_item.parent_contract_item = None        
    #     contract_item.is_group = 1
    #     contract_item.codigo = f"Contrato {contract_data['contrato']}"
    #     contract_item.descricao = f"Contrato {contract_data['contrato']}"
    #     contract_item.contrato = contract_data["name"]
    #     result = contract_item.save()