import frappe
from typing import Dict, Any

@frappe.whitelist()
def get_measurement_data(uuid: str) -> Dict[str, Any]:
    """
    Get measurement data for Frappe custom page
    This replaces the get_data_remote function using Frappe's database functions
    """
    data = {}

    # Get contract total value
    contract = frappe.get_doc('Contract', uuid)
    valor_total_contrato = contract.valortotal
    data['valor_total_contrato'] = valor_total_contrato

    # Get contract items
    contract_items_list = frappe.get_all(
        'Contract Item',
        filters={'contrato': uuid},
        fields=['name', 'codigo', 'descricao', 'unidade', 'quantidade', 'valorunitario', 'valortotalvigente'],
        order_by='codigo'
    )

    # Add level calculation to contract items
    for item in contract_items_list:
        item['level'] = calculate_contract_item_level(item.get('codigo', ''))

    # Assign sum of all children if valortotalvigente is missing or zero
    for idx, item in enumerate(contract_items_list):
        codigo = item.get('codigo')
        valor = item.get('valortotalvigente', 0)
        if not valor or valor == 0:
            # Find all children whose 'codigo' starts with this 'codigo' + '.'
            children_sum = sum(
                child.get('valortotalvigente', 0)
                for child in contract_items_list
                if child.get('codigo', '').startswith(f"{codigo}.") and child.get('codigo') != codigo
            )
            contract_items_list[idx]['valortotalvigente'] = children_sum

    # Get contract measurements
    contract_measurements = frappe.get_all(
        'Contract Measurement',
        filters={'contrato': uuid},
        fields=['name'],
        order_by='datafinalmedicao'
    )

    contract_measurement_list = []
    valor_total_periodo = 0.0
    valor_total_acumulado = 0.0
    medicao_acumulada = 0.0
    
    # Create a map of item names to indices once before the loop
    item_index_map = {item['name']: index for index, item in enumerate(contract_items_list)}

    for measurement_ref in contract_measurements:
        # Get full measurement document
        contract_measurement = frappe.get_doc('Contract Measurement', measurement_ref['name'])
        
        # Convert to dict for easier manipulation
        measurement_dict = contract_measurement.as_dict()
        
        valor_total_periodo += measurement_dict.get('valortotalmedido', 0)
        valor_total_acumulado += measurement_dict.get('valortotalvigente', 0)
        data['medicaoacumulada'] = measurement_dict.get('medicaoacumulada', 0)

        data['valor_total_periodo'] = valor_total_periodo
        data['valor_total_acumulado'] = valor_total_acumulado

        # Initialize contract measurement items list
        contract_measurement_contract_items_list = [{} for _ in range(len(contract_items_list))]
        show_pay_factor = False
        
        # Process measurement items (assuming tabitenscontatrato is a child table)
        for contract_item in measurement_dict.get('tabitenscontatrato', []):
            ordered_list_index = item_index_map.get(contract_item.get('itemcontrato'))
            
            if ordered_list_index is not None:
                level = contract_items_list[ordered_list_index]['level']
                contract_item['level'] = level
                contract_item['codigo'] = contract_items_list[ordered_list_index]['codigo']

                if contract_item.get('valorfatorpagamento') and contract_item.get('valorfatorpagamento') != 0:
                    show_pay_factor = True
                
                contract_measurement_contract_items_list[ordered_list_index] = contract_item

        # Fill empty items with basic info
        for index, contract_item in enumerate(contract_measurement_contract_items_list):
            if contract_item == {}:
                contract_measurement_contract_items_list[index]['codigo'] = contract_items_list[index]['codigo']
                contract_measurement_contract_items_list[index]['level'] = contract_items_list[index]['level']

        # Calculate parent sums for missing values
        for idx, item in enumerate(contract_measurement_contract_items_list):
            codigo = item.get('codigo')
            
            # Sum valortotalmedido
            valor_medido = item.get('valortotalmedido', 0)
            if not valor_medido or valor_medido == 0:
                children_sum = sum(
                    child.get('valortotalmedido', 0)
                    for child in contract_measurement_contract_items_list
                    if child.get('codigo', '').startswith(f"{codigo}.") and child.get('codigo') != codigo
                )
                contract_measurement_contract_items_list[idx]['valortotalmedido'] = children_sum

            # Sum valortotalvigente
            valor_vigente = item.get('valortotalvigente', 0)
            if not valor_vigente or valor_vigente == 0:
                children_sum_vigente = sum(
                    child.get('valortotalvigente', 0)
                    for child in contract_measurement_contract_items_list
                    if child.get('codigo', '').startswith(f"{codigo}.") and child.get('codigo') != codigo
                )
                contract_measurement_contract_items_list[idx]['valortotalvigente'] = children_sum_vigente

        # Update measurement dict
        measurement_dict['pay_factor_exist'] = show_pay_factor
        measurement_dict['tabitenscontatrato'] = contract_measurement_contract_items_list
        
        contract_measurement_list.append(measurement_dict)

    data['contract_measurement_list'] = contract_measurement_list
    data['contract_items_list'] = contract_items_list
    
    # Calculate percentage
    if valor_total_contrato and valor_total_contrato > 0:
        data['medicao_atual_acumulada_percentual'] = (data.get('medicaoacumulada', 0) / valor_total_contrato) * 100
    else:
        data['medicao_atual_acumulada_percentual'] = 0

    return data

def calculate_contract_item_level(code: str) -> int:
    """Calculate the level of a contract item based on its code structure"""
    if not code:
        return 0
    return code.count('.') + 1

# Alternative method using SQL queries for better performance
@frappe.whitelist()
def get_measurement_data_optimized(uuid: str) -> Dict[str, Any]:
    """
    Optimized version using SQL queries for better performance
    """
    data = {}
    
    # Get contract total value
    contract_data = frappe.db.get_value('Contract', uuid, 'valortotal')
    data['valor_total_contrato'] = contract_data or 0
    
    # Get contract items using SQL
    contract_items = frappe.db.sql("""
        SELECT name, codigo, descricao, unidade, quantidade, valorunitario, valortotalvigente
        FROM `tabContract Item`
        WHERE contrato = %s
        ORDER BY codigo
    """, (uuid,), as_dict=True)
    
    # Add level calculation
    for item in contract_items:
        item['level'] = calculate_contract_item_level(item.get('codigo', ''))
    
    # Calculate parent sums for contract items
    for idx, item in enumerate(contract_items):
        codigo = item.get('codigo')
        valor = item.get('valortotalvigente', 0)
        if not valor or valor == 0:
            children_sum = sum(
                child.get('valortotalvigente', 0)
                for child in contract_items
                if child.get('codigo', '').startswith(f"{codigo}.") and child.get('codigo') != codigo
            )
            contract_items[idx]['valortotalvigente'] = children_sum
    
    # Get contract measurements
    measurements = frappe.db.sql("""
        SELECT name, datafinalmedicao, valortotalmedido, valortotalvigente, medicaoacumulada
        FROM `tabContract Measurement`
        WHERE contrato = %s
        ORDER BY datafinalmedicao
    """, (uuid,), as_dict=True)
    
    contract_measurement_list = []
    medicao_acumulada = 0.0
    
    for measurement in measurements:
        # Get measurement items (child table)
        measurement_items = frappe.db.sql("""
            SELECT itemcontrato, quantidademedida, quantidadetotalvigente, 
                   valortotalmedido, valortotalvigente, valorfatorpagamento
            FROM `tabContract Measurement Item`
            WHERE parent = %s
        """, (measurement['name'],), as_dict=True)
        
        # Process measurement items similar to original logic
        item_index_map = {item['name']: index for index, item in enumerate(contract_items)}
        contract_measurement_contract_items_list = [{} for _ in range(len(contract_items))]
        show_pay_factor = False
        
        for item in measurement_items:
            ordered_list_index = item_index_map.get(item.get('itemcontrato'))
            
            if ordered_list_index is not None:
                item['level'] = contract_items[ordered_list_index]['level']
                item['codigo'] = contract_items[ordered_list_index]['codigo']
                
                if item.get('valorfatorpagamento') and item.get('valorfatorpagamento') != 0:
                    show_pay_factor = True
                
                contract_measurement_contract_items_list[ordered_list_index] = item
        
        # Fill empty items and calculate sums (same logic as before)
        for index, item in enumerate(contract_measurement_contract_items_list):
            if item == {}:
                contract_measurement_contract_items_list[index]['codigo'] = contract_items[index]['codigo']
                contract_measurement_contract_items_list[index]['level'] = contract_items[index]['level']
        
        # Calculate parent sums
        for idx, item in enumerate(contract_measurement_contract_items_list):
            codigo = item.get('codigo')
            
            # Sum valortotalmedido
            valor_medido = item.get('valortotalmedido', 0)
            if not valor_medido or valor_medido == 0:
                children_sum = sum(
                    child.get('valortotalmedido', 0)
                    for child in contract_measurement_contract_items_list
                    if child.get('codigo', '').startswith(f"{codigo}.") and child.get('codigo') != codigo
                )
                contract_measurement_contract_items_list[idx]['valortotalmedido'] = children_sum
            
            # Sum valortotalvigente
            valor_vigente = item.get('valortotalvigente', 0)
            if not valor_vigente or valor_vigente == 0:
                children_sum_vigente = sum(
                    child.get('valortotalvigente', 0)
                    for child in contract_measurement_contract_items_list
                    if child.get('codigo', '').startswith(f"{codigo}.") and child.get('codigo') != codigo
                )
                contract_measurement_contract_items_list[idx]['valortotalvigente'] = children_sum_vigente
        
        measurement['pay_factor_exist'] = show_pay_factor
        measurement['tabitenscontatrato'] = contract_measurement_contract_items_list
        measurement['valor_total_periodo'] = sum(item.get('valortotalmedido', 0) for item in measurement_items)
        measurement['valor_total_acumulado'] = sum(item.get('valortotalvigente', 0) for item in measurement_items)
        
        contract_measurement_list.append(measurement)
        medicao_acumulada = measurement.get('medicaoacumulada', 0)
    
    data['contract_measurement_list'] = contract_measurement_list
    data['contract_items_list'] = contract_items
    data['medicaoacumulada'] = medicao_acumulada
    
    # Calculate percentage
    if data['valor_total_contrato'] and data['valor_total_contrato'] > 0:
        data['medicao_atual_acumulada_percentual'] = (medicao_acumulada / data['valor_total_contrato']) * 100
    else:
        data['medicao_atual_acumulada_percentual'] = 0
    
    return data