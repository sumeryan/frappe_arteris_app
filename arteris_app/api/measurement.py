import frappe
from frappe.utils import add_to_date
from datetime import datetime, timedelta, date

@frappe.whitelist(methods=["GET"])
def close_measurements(contract: str):
    """
    Get current 
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
    measurement = measurement.replace("\r","")

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

    holidays = {}

    # Function to check if a date is a holiday
    def check_holiday(date: date, uf: str, city: str):

        key = f"{date.strftime('%Y-%m-%d')}-{city}-{uf}"
        if holidays.get(key, None) == None:
            if not city == "all":
                get_result = frappe.db.get_all("Holiday", fields=["data","descricao"], filters={"data": date, "cidade": city})
            elif not uf == "all":
                get_result = frappe.db.get_all("Holiday", fields=["data","descricao"], filters={"data": date, "uf": uf})
            else:
                get_result = frappe.db.get_all("Holiday", fields=["data","descricao"], filters={"data": date, "uf": "", "cidade": ""})
            if get_result:
                holidays[key] = {
                     "isholiday": True,
                     "uf": "" if uf == "all" else uf,
                     "cidade": "" if city == "all" else city,
                     "descricao": get_result[0].descricao
                }
            else:
                holidays[key] = {
                     "isholiday": False
                }
        return holidays[key]

    def check_holidays(date: date, city: str = None):

        # City and UF is a key of city
        uf = "all"
        if city:
            s_sity = city.split("-")
            uf = s_sity[1]
            city = s_sity[0]
        else:
            city = "all"
            uf = "all"

        # Check if the date is a holiday
        holiday = check_holiday(date, "all", "all")
        if holiday['isholiday']:
            return holiday
        holiday = check_holiday(date,  uf, "all")
        if check_holiday(date, uf, "all"):
            return holiday
        holiday = check_holiday(date, "all", city)
        if check_holiday(date, "all", city):
            return holiday

    def get_busy_days(start_date: date, end_date: date, city: str = None) -> int:

        busy_days = 0
        
        while start_date < end_date:
            holiday = check_holidays(start_date, city)
            if not holiday['isholiday']:
                # 0-4 is business days (Monday to Friday)
                if start_date.weekday() < 5:  
                    busy_days += 1
            start_date += timedelta(days=1)
        
        return busy_days

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
                # frappe.log_error(f"Error getting last contract measurement: {str(e)}", "Create Measurement Error")

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

            s_first_day = first_day.split("-")
            s_last_day = last_day.split("-")

            contract_measurement = frappe.new_doc("Contract Measurement")
            contract_measurement.name = f"BM-{contract.contrato}-{s_first_day[2]}-{s_last_day[2]}-{s_last_day[1]}-{s_last_day[2]}"
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
            get_contract_items = frappe.db.get_all("Contract Item", fields=["*"], filters={"contrato": contract.name, "is_group": False})

            for item in get_contract_items:

                busy_days = get_busy_days(
                    datetime.strptime(first_day, "%Y-%m-%d"), 
                    datetime.strptime(last_day, "%Y-%m-%d"), 
                    item.cidade)

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
                contract_measurement_item.cidade = item.cidade
                contract_measurement_item.diasuteis = busy_days
                contract_measurement_item.valorunitario = item.valorunitario

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
                            contract_measurement_work_role.valorunitario = 0.0


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
                            contract_measurement_asset.valorunitario = 0.0

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
def update_measurement_records(measurement: str):
    """
    Sum all measurement orders for a given measurement.
    """
    count_update = 0

    # Get the measurement document
    measurement_doc = frappe.get_doc("Contract Measurement", measurement)
    # Get contract items
    contract_items = frappe.db.get_all("Contract Item", fields=["name","valorunitario","tipodoitem","codigo"], filters={"contrato": measurement_doc.contrato})
    # Get item work roles
    contract_item_work_roles = frappe.db.get_all("Contract Item Work Role", fields=["name","parent","funcao","pagamentohora","valorporhora", "valortotalmensal"], filters={"parent": ["in", [item.name for item in contract_items]]})
    # Get item assets
    contract_item_assets = frappe.db.get_all("Contract Item Asset", fields=["name","parent","asset","valormensal"], filters={"parent": ["in", [item.name for item in contract_items]]})
    # Unir price list
    price_list = {}
    # Update measurement items only if the measurement is active
    if measurement_doc.medicaovigente == "Sim":
        # Get all contract items measurement
        for item in contract_items:
            # Update maesurement items
            for item_measurement in measurement_doc.tabitenscontatrato:
                if item_measurement.itemcontrato == item.name:
                    # Update unit price
                    price_list[f"{item.name}-{item.name}"] = item.valorunitario                    
                    frappe.db.set_value("Contract Measurement Item", measurement_doc.name, "valorunitario", item.valorunitario)
            # Update work roles
            for work_role_measurement in measurement_doc.tablemaodeobra:
                # if work_role_measurement.item == item.name
                for work_role in contract_item_work_roles:
                    # Check if the work role is in the item
                    if work_role_measurement.item == item.name and work_role_measurement.funcao == work_role.funcao:
                        # Update unit price
                        if work_role.pagamentohora:
                            price_list[f"{item.name}-{work_role.funcao}"] = work_role.valorporhora
                        else:
                            price_list[f"{item.name}-{work_role.funcao}"] = work_role.valortotalmensal
                        frappe.db.set_value("Contract Measurement Work Role", work_role_measurement.name, "valorunitario", price_list[f"{item.name}-{work_role.funcao}"])
            # Update assets
            for asset_measurement in measurement_doc.tableativos:
                # if asset_measurement.item == item.name
                for asset in contract_item_assets:
                    # Check if the asset is in the item
                    if asset_measurement.item == item.name and asset_measurement.maquina_equipamento_ou_ferramenta == asset.asset:
                        # Update unit price
                        price_list[f"{item.name}-{asset.asset}"] = asset.valormensal
                        frappe.db.set_value("Contract Measurement Asset", asset_measurement.name, "valorunitario", asset.valormensal)
    else:
        # Get maesurement items values
        for item_measurement in measurement_doc.tabitenscontatrato:
            price_list[f"{item_measurement.item}-{item_measurement.item}"] = item_measurement.valorunitario
        # Get work roles values
        for work_role_measurement in measurement_doc.tablemaodeobra:
            price_list[f"{work_role_measurement.item}-{work_role_measurement.funcao}"] = work_role_measurement.valorunitario
        # Get assets values
        for asset_measurement in measurement_doc.tableativos:
            price_list[f"{asset_measurement.item}-{asset_measurement.maquina_equipamento_ou_ferramenta}"] = asset_measurement.valorunitario

    # Get all measurement records for the measurement
    parent_records = frappe.db.get_all("Contract Measurement Record", fields=["name","equipe"], filters={"boletimmedicao": measurement})
    for parent_record in parent_records:
        # Count the number of updates
        count_update += 1
        # Update calculated value for measurement records
        child_doctypes = [
            { "doctype":"Contract Measurement Record Asset", "field": "maquina_equipamento_ou_ferramenta"},
            { "doctype":"Contract Measurement Record Material", "field": "material"},
            { "doctype":"Contract Measurement Record Work Role", "field": "funcao"},
            { "doctype":"Contract Measurement Record Resource", "field": "item"},
        ]
        # Update calculated value for each measurement record type
        for doctype in child_doctypes:
            # Get all child records for the measurement record
            child_records = frappe.db.get_all(doctype['doctype'], fields=["name", "item" ,"quantidademedida", "valorcalculado",doctype['field']], filters={"parent": parent_record.name})
            for child_record in child_records:
                # Check if the child record is in the price list
                if f"{child_record.item}-{child_record[doctype['field']]}" in price_list:
                    child_record["valorcalculado"] = child_record["quantidademedida"] * price_list[f"{child_record.item}-{child_record[doctype['field']]}"]
                else:
                    child_record["valorcalculado"] = 0.0
                # Set the value in the database
                frappe.db.set_value(doctype['doctype'], child_record.name, "valorcalculado", child_record["valorcalculado"])

    return {"Processed": True, "message": "Records updated successfully.", "count": count_update}

@frappe.whitelist(methods=["POST"])
def update_contract_measurement_records(contract: str = None):
    """
    Get all open measurements for a given contract.
    """
    filters = {"medicaovigente": "Sim"}
    if contract:
        filters["contrato"] = contract

    measurements = frappe.db.get_all("Contract Measurement", fields=["name"], filters=filters)

    for measurement in measurements:
        return_measurements = update_measurement_records(measurement.name)

    return return_measurements

@frappe.whitelist(methods=["POST"])
def sumarize_measurements(contract: str = None):
    """
    Get all open measurements for a given contract.
    """
    filters = {"medicaovigente": "Sim"}
    if contract:
        filters["contrato"] = contract

    measurements = frappe.db.get_all("Contract Measurement", fields=["name"], filters=filters)

    for measurement in measurements:
        sum_measurement_orders(measurement.name)

    return measurements

@frappe.whitelist(methods=["POST"])
def sum_measurement_orders(measurement: str):
    """
    Sum all measurement orders for a given measurement.
    """
    # Get the measurement document
    measurement_doc = frappe.get_doc("Contract Measurement", measurement)

    # Get contract SAP orders
    contract_item_sap_orders = []
    contract_itens = frappe.db.get_all("Contract Item", fields=["name","codigo"], filters={"contrato": measurement_doc.contrato})

    for item in contract_itens:

        item_order = {"name": item.name, "code": item.codigo, "total": 0.0, "sap_orders": []}
        
        # Get all SAP orders for the contract item
        sap_orders = frappe.db.get_all("Contract Item Order", fields=["name","valortotal","pedidosap"], filters={"parent": item.name})
        for item_sap_order in sap_orders:
            # Add the SAP order to the list
            item_order["sap_orders"].append(
                {
                    "name": item_sap_order.name,
                    "pedidosap": item_sap_order.pedidosap,
                    "value": item_sap_order.valortotal,
                    "total": 0.0
                }) 

        if len(item_order["sap_orders"]):
            contract_item_sap_orders.append(
                {
                    "name": item.name, 
                    "code": item.codigo,
                    "total": 0.0, 
                    "sap_orders": [o for o in item_order["sap_orders"]]
                })

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

    # Get SAP orders for the item
    measurements_sap = frappe.db.get_all("Contract Measurement SAP Order", fields=["name","pedido_sap"], filters={"parent": measurement})

    # Update measurement total value
    for item_sap_order in contract_item_sap_orders:

        for item_measurement in measurement_itens:
            if item_measurement.name == item_sap_order["name"]:
                for sap_order in item_sap_order["sap_orders"]:
                    sap_order["total"] = item_measurement.valortotalmedido * sap_order["factor"]

        for measurement_sap in measurements_sap:
            # Get the total value for the item
            for sap_order in item_sap_order["sap_orders"]:
                if sap_order["pedidosap"] == measurement_sap.pedido_sap:
                    sap_doc = frappe.get_doc("Contract Measurement SAP Order", measurement_sap["name"])
                    sap_doc.valormedido = sap_order["total"]
                    if sap_doc.valortotalvigente == 0.0:
                        sap_doc.valortotalvigente = sap_order["value"]
                    sap_doc.valormedido = sap_order["total"]
                    sap_doc.acumuladoatual = sap_doc.valormedido + sap_doc.acumuladoanterior
                    if sap_doc.valortotalvigente > 0:
                        sap_doc.medicaoacumuladaatualpercentual = sap_doc.acumuladoatual / sap_doc.valortotalvigente * 100.0
                    sap_doc.save()

    return {"Processed": True, "message": "Measurement orders summed successfully."}