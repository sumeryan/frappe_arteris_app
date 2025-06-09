import frappe
from frappe.utils import add_to_date

@frappe.whitelist(methods=["POST"])
def close_measurements(contract: str):
    """
    Close all measurements for a given contract.
    """
    # Get all measurements for the contract
    measurements = frappe.db.get_all("Contract Measurement", fields=["name"], filters={"contrato": contract, "medicaovigente": "Sim"})

    if not measurements:
        return {"message": f"No open measurements found for contract {contract}."}

    # Close each measurement
    for measurement in measurements:
        doc = frappe.get_doc("Contract Measurement", measurement.name)
        doc.medicaovigente = "Não"
        doc.save()
        # Close all measurement records associated with this measurement
        measurement_records = frappe.db.get_all("Contract Measurement Record", fields=["name"], filters={"boletimmedicao": measurement.name, "medicaovigente": "Sim"})
        for record in measurement_records:
            record_doc = frappe.get_doc("Contract Measurement Record", record.name)
            record_doc.medicaovigente = "Não"
            record_doc.save()

    return {"message": f"Closed {len(measurements)} measurements for contract {contract}."}

@frappe.whitelist(methods=["POST"])
def open_measurement(measurement: str):
    """
    Open measurement.
    """
    # Get all measurements for the contract
    measurements = frappe.db.get_all("Contract Measurement", fields=["name","contrato"], filters={"name": measurement})

    # Close the measurement if it is open
    close_measurements(measurements[0].contrato) 

    if not measurements:
        return {"message": f"No measurements found for name {measurement}."}

    # Open each measurement
    for measurement in measurements:
        doc = frappe.get_doc("Contract Measurement", measurement.name)
        doc.medicaovigente = "Sim"
        doc.save()
        # Open all measurement records associated with this measurement
        measurement_records = frappe.db.get_all("Contract Measurement Record", fields=["name"], filters={"boletimmedicao": measurement.name})
        for record in measurement_records:
            record_doc = frappe.get_doc("Contract Measurement Record", record.name)
            record_doc.medicaovigente = "Sim"
            record_doc.save()

    return {"message": f"Open measurement {measurement}."}

@frappe.whitelist(methods=["POST"])
def create_measurement(month: int, year: int, ignore_current_measurement: bool = False, contract: str = None):

    # Get all contracts
    if contract:
        get_contracts = frappe.db.get_all("Contract", fields=["*"], filters={"contratoencerrado": None, "name": contract})
    else:
        get_contracts = frappe.db.get_all("Contract", fields=["*"], filters={"contratoencerrado": None})

    measurements = []
    inconsistencies = []

    # Get all contracts
    for contract in get_contracts:

        if (contract.medicaodiainicial == 0 or contract.medicaodiafinal == 0) and (contract.medicaopormes == 0):
            inconsistencies.append(f"Contract {contract.name} does not have valid measurement dates.")
            continue

        if contract.medicaopormes == 0:
            first_day = f"{year:04d}-{month:02d}-{contract.medicaodiainicial:02d}"
            if month == 12:
                last_day = f"{year + 1:04d}-{1:02d}-{contract.medicaodiafinal:02d}"
            else:
                last_day = f"{year:04d}-{month + 1:02d}-{contract.medicaodiafinal:02d}"
        else:
            first_day = f"{year:04d}-{month:02d}-01"
            last_day = add_to_date(add_to_date(first_day, months = 1, as_string = True),days = -1, as_string = True)
        
        # Check open measurement
        if not ignore_current_measurement:
            existing_measurements = frappe.db.get_all("Contract Measurement", filters={
                "medicaovigente": "Sim",
                "contrato": contract.name
            })        
            if existing_measurements:
                inconsistencies.append(f"Contract Measurement already exists for contract {contract.name}")
                continue

        # Check existing measurements for the month and year
        existing_measurements = frappe.db.get_all("Contract Measurement", fields=["name","datainicialmedicao","datafinalmedicao","medicaovigente"], filters={
            "datainicialmedicao": first_day,
            "datafinalmedicao": last_day,
            "contrato": contract.name
        })

        if not existing_measurements:

            try:
                last_contract_measurement = frappe.frappe.get_last_doc("Contract Measurement")
            except Exception as e:
                last_contract_measurement = None
                frappe.log_error(f"Error getting last contract measurement: {str(e)}", "Create Measurement Error")

            medicaoacumulada = 0.0
            caucaoacumulado = 0.0
            ftdacumulado = 0.0

            if last_contract_measurement:
                # Get last measurement values
                medicaoacumulada = last_contract_measurement.medicaoacumulada
                caucaoacumulado = last_contract_measurement.caucaoacumulado
                ftdacumulado = last_contract_measurement.ftdacumulado

            # Close existing measurements if they are open
            close_measurements(contract.name)

            contract_measurement = frappe.new_doc("Contract Measurement")
            contract_measurement.contrato = contract.name
            contract_measurement.datainicialmedicao = first_day
            contract_measurement.datafinalmedicao = last_day
            contract_measurement.medicaovigente = "Sim"
            contract_measurement.data_ejak = contract.datainicial
            contract_measurement.obra = contract.obra
            contract_measurement.valorcontrato = contract.valortotal
            contract_measurement.medicaoatual = 0.0
            contract_measurement.faturamentodireto = 0.0
            contract_measurement.medicaoatualdescontoftd = 0.0
            contract_measurement.descontoreidi = 0.0
            contract_measurement.medicaoliquida = 0.0
            contract_measurement.medicaoequivalente = 0.0
            contract_measurement.caucaocontratual = 0.0
            contract_measurement.valortotalvigente = contract.valortotal
            contract_measurement.ftdacumulado = 0.0
            contract_measurement.totalvigentemenosftd = 0.0
            contract_measurement.medicaoacumulada = 0.0
            contract_measurement.saldo = 0.0
            contract_measurement.saldopercentual = 0.0
            contract_measurement.caucaoatual = 0.0
            contract_measurement.caucaoacumulado = 0.0
            contract_measurement.medicaoacumuladaanterior = medicaoacumulada
            contract_measurement.caucaoacumuladoanterior = caucaoacumulado
            contract_measurement.ftdacumuladoanterior = ftdacumulado
            

            # Get Contract Items
            get_contract_items = frappe.db.get_all("Contract Item", fields=["*"], filters={"contrato": contract.name})

            for item in get_contract_items:

                # Set the value to valortotalvigente if it is 0.0
                if item.valortotalvigente == 0.0:
                    if item.quantidade:
                        item.quantidade = 0.0
                    if item.valorunitario:
                        item.valorunitario = 0.0
                    item.valortotalvigente = item.quantidade * item.valorunitario

                saldo = 0.0
                valortotalacumulado = 0.0
                quantidadeacumulada = 0.0

                # Get last contract measurement item
                if last_contract_measurement:

                    try:
                        last_measurement_item = frappe.get_last_doc("Contract Measurement Item", filters={"itemcontrato": item.name, "parent": last_contract_measurement.name})
                    except Exception as e:
                        last_measurement_item = None
                        frappe.log_error(f"Error getting last contract measurement item: {str(e)}", "Create Measurement Error")

                    if last_measurement_item:
                        saldo = last_measurement_item.saldoatual
                        valortotalacumulado = last_measurement_item.valortotalmedido
                        quantidadeacumulada = last_measurement_item.quantidademedida

                # Mount the contract item to the contract measurement
                contract_measurement_item = contract_measurement.append("tabitenscontatrato")
                contract_measurement_item.itemcontrato = item.name
                contract_measurement_item.valortotalvigente = item.valortotalvigente
                contract_measurement_item.quantidadetotalvigente = item.quantidade
                contract_measurement_item.saldoanterior = saldo
                contract_measurement_item.quantidademedida = 0.0
                contract_measurement_item.valortotalmedido = 0.0
                contract_measurement_item.saldoatual = 0.0
                contract_measurement_item.valortotalacumuladoanterior = valortotalacumulado
                contract_measurement_item.quantidadeacumuladaanterior = quantidadeacumulada                
                contract_measurement_item.valortotalacumulado = 0.0
                contract_measurement_item.quantidadeacumulada = 0.0
                contract_measurement_item.fatorpagamento = 100.0
                contract_measurement_item.valorfatorpagamento = item.valorunitario

                # Get SAP Orders
                item_sap_orders = frappe.db.get_all("Contract Item Order", fields=["*"], filters={"parent": item.name})
                if item_sap_orders:
                    for sap_order in item_sap_orders:

                        # Get SAP Order Lines
                        get_sap_orders = frappe.db.get_all("SAP Order Period", fields=["*"], filters={"parent": sap_order.pedidosap})
                        for sap_order_line in get_sap_orders:
                            # Compare year
                            if sap_order_line.datainicial.year == int(first_day[:4]):
                                # Add only if not exists
                                if not sap_order_line.name in contract_measurement.tablepedidossap:

                                    medicaoacumantpercentual = 0.0
                                    acumuladoanterior = 0.0

                                    # Get last contract measurement SAP Order
                                    if last_contract_measurement:

                                        try:
                                            last_contract_measurement_sap_order = frappe.get_last_doc("Contract Measurement SAP Order", filters={"pedido_sap": sap_order.pedidosap, "linhapedido": sap_order_line.name, "parent": last_contract_measurement.name})
                                        except Exception as e:
                                            last_contract_measurement_sap_order = None
                                            frappe.log_error(f"Error getting last contract measurement SAP order: {str(e)}", "Create Measurement Error")
                                        
                                        if last_contract_measurement_sap_order:
                                            medicaoacumantpercentual = last_contract_measurement_sap_order.medicaoacumantpercentual
                                            acumuladoanterior = last_contract_measurement_sap_order.acumuladoatual

                                    # Mount the SAP Order to the contract measurement
                                    contract_measurement_sap_order = contract_measurement.append("tablepedidossap")
                                    contract_measurement_sap_order.pedido_sap = sap_order.pedidosap
                                    contract_measurement_sap_order.linhapedido = sap_order_line.name
                                    contract_measurement_sap_order.valortotalvigente = sap_order_line.valortotalvigente
                                    contract_measurement_sap_order.medicaoacumantpercentual = medicaoacumantpercentual
                                    contract_measurement_sap_order.medicaoatualpercentual = 0.0
                                    contract_measurement_sap_order.medicaoacumuladaatualpercentual = 0.0
                                    contract_measurement_sap_order.acumuladoanterior = acumuladoanterior
                                    contract_measurement_sap_order.valormedido = 0.0
                                    contract_measurement_sap_order.acumuladoatual = 0.0

                # Get Work Role
                item_work_roles = frappe.db.get_all("Contract Item Work Role", fields=["*"], filters={"parent": item.name})
                if item_work_roles:
                    for work_role in item_work_roles:
                        if not item.item in contract_measurement.tablemaodeobra:
                            # Mount the Work Role to the contract measurement
                            contract_measurement_work_role = contract_measurement.append("tablemaodeobra")
                            contract_measurement_work_role.item = item.name
                            contract_measurement_work_role.funcao = work_role.funcao
                            contract_measurement_work_role.quantidademedida = 0.0
                            contract_measurement_work_role.valormedido = 0.0


                # Get Asset
                item_assets = frappe.db.get_all("Contract Item Asset", fields=["*"], filters={"parent": item.name})
                if item_assets:
                    for asset in item_assets:
                        if not item.item in contract_measurement.tableativos:
                            # Mount the Asset to the contract measurement
                            contract_measurement_asset = contract_measurement.append("tableativos")
                            contract_measurement_asset.item = item.name
                            contract_measurement_asset.maquina_equipamento_ou_ferramenta = asset.asset
                            contract_measurement_asset.quantidademedida = 0.0
                            contract_measurement_asset.valormedido = 0.0

            # Add the contract measurement to the database
            m = contract_measurement.save()
            measurements.extend([{"name": m.name, "contract": contract.name, "start": m.datainicialmedicao, "end": m.datafinalmedicao, "current": m.medicaovigente}])
        else:
            m = existing_measurements[0]
            measurements.extend([{"name": m.name, "contract": contract.name, "start": m.datainicialmedicao, "end": m.datafinalmedicao, "current": m.medicaovigente}])

    return {
        "measurements": measurements,
        "inconsistencies": inconsistencies
    }

@frappe.whitelist(methods=["POST"])
def sum_measurement_orders(measurement: str):
    """
    Sum all measurement orders for a given measurement.
    """
    # Get the measurement document
    measurement_doc = frappe.get_doc("Contract Measurement", measurement)

    # Get contract SAP orders
    contract_item_sap_orders = []
    contract_itens = frappe.db.get_all("Contract Item", fields=["name"], filters={"contrato": measurement_doc.contrato})

    for item in contract_itens:
        item_order = {"name": item.name, "total": 0.0, "sap_orders": []}
        # Get all SAP orders for the contract item
        sap_orders = frappe.db.get_all("Contract Item Order", fields=["name"], filters={"parent": item.name})
        for item_sap_order in sap_orders:
            # Add the SAP order to the list
            item_order["sap_orders"].append({"name": item_sap_order.name, "value": item_sap_order.valortotal, "total": 0.0})
        
        contract_item_sap_orders.extend(item_order.copy())

    # Sum and get the factor for each SAP order
    for item_sap in contract_item_sap_orders:
        order_total = 0.0
        for item_sap_order in item_sap["sap_orders"]:
            order_total += item_sap_order["value"]
        # Get the factor for each SAP order
        for item_sap_order in item_sap["sap_orders"]:
            item_sap_order["factor"] = item_sap_order["value"] / order_total
 
    # Get all itens measurement totals
    measurement_itens = frappe.db.get_all("Contract Measurement Item", fields=["name","valortotalmedido"], filters={"parent": measurement})

    # Update measurement total value
    for item_sap_order in contract_item_sap_orders:

        for item_measurement in measurement_itens:
            if item_measurement.name == item_sap_order["name"]:
                for sap_order in item_sap_order["sap_orders"]:
                    sap_order["total"] = item_measurement.valortotalmedido * sap_order["factor"]

        # Get SAP orders for the item
        measurements_sap = frappe.db.get_all("", fields=["name"], filters={"parent": measurement})

        for measurement_sap in measurements_sap:
            # Get the total value for the item
            for item in item_sap_order:
                for sap_order in item["sap_orders"]:
                    if sap_order["name"] == measurement_sap.name:
                        sap_doc = frappe.get_doc("Contract Measurement SAP Order", sap_order["name"])
                        sap_doc.valormedido = sap_order["total"]
                        sap_doc.acumuladoatual = sap_doc.valormedido + sap_doc.acumuladoanterior
                        sap_doc.medicaoacumuladaatualpercentual = sap_doc.acumuladoatual / sap_doc.valortotalvigente * 100.0
                        sap_doc.save()

    return {"Processed": True, "message": "Measurement orders summed successfully."}