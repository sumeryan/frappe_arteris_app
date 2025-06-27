import frappe
from frappe import _

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

            pedidosSap = []

            unique_pedidos = {}
            tabelaPedidos = doc.tablepedidossap
            pedido_sap_ids = []

            # Filter unique pedidos by pedido_sap
            for pedido in tabelaPedidos:
                sap_id = pedido.pedido_sap
                if sap_id not in unique_pedidos:
                    unique_pedidos[sap_id] = pedido
                    pedido_sap_ids.append(sap_id)

            sap_orders = frappe.get_all(
                'SAP Order',
                filters={'name': ['in', list(pedido_sap_ids)]},
                fields=['*']  # Removed 'table_dscc' from fields
            )

            # Fetch full SAP Order docs to access child tables
            for sap_order_meta in sap_orders:
                sap_order_doc = frappe.get_doc('SAP Order', sap_order_meta['name'])
                detalhePedido = flatten_sap_order(sap_order_doc.as_dict())
                pedidosSap.extend(detalhePedido)

            context.pedidos_sap_json = frappe.as_json(pedidosSap)

        except frappe.DoesNotExistError:
            frappe.throw(_("Contract Measurement not found"), frappe.DoesNotExistError)
    else:
        frappe.throw(_("No id provided in URL"), frappe.DoesNotExistError)
    return context

def flatten_sap_order(json_data):
    """
    Flatten SAP order data by combining header with period data.
    
    Args:
        json_data: Dictionary containing SAP order data
        
    Returns:
        List of flattened dictionaries combining header and period data
    """
    # Verify json_data is a dictionary
    if not isinstance(json_data, dict):
        print(f"Error: Expected dictionary but got {type(json_data)}")
        return []

    # Safely get the data dictionary
    data = json_data
    if not data:
        print("Warning: No 'data' key found in json_data")
        return []

    # Create a copy of the header data
    header = data.copy()
    
    # Safely remove the nested arrays from header
    periods = header.pop('table_dscc', [])
    header.pop('table_nqgi', [])  # Remove but don't store
    
    # Create flattened array
    flattened = []
    
    # If no periods found, return the header data alone
    if not periods:
        print("Warning: No periods found in table_dscc")
        return [header]
    
    try:
        for period in periods:
            # Combine header data with each period
            combined_item = {**header, **period}
            flattened.append(combined_item)
    except Exception as e:
        print(f"Error while processing periods: {str(e)}")
        return [header]
    
    return flattened