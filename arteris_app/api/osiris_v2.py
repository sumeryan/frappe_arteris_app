import frappe
from datetime import date, datetime

@frappe.whitelist(methods=["GET"])
def get_process(start_date: str):

    sql = f"""
            SELECT 
                name 
            FROM 
                `tabContract`
            WHERE 
                datainiciomedicao <= '{start_date}'
                AND contratoencerrado IS NULL 
            """

    contracts_to_process = frappe.db.sql(sql, as_dict=True)

    if not contracts_to_process:
        print("No contracts to process.")
        return

    return contracts_to_process

@frappe.whitelist(methods=["DELETE"])
def clear_keys():
    """
    Clear all keys from the database.
    """
    get_result = frappe.db.get_all("Integration Record", fields=["name"], filters={"tipo": "Osiris"})
    for record in get_result:
        doc = frappe.get_doc("Integration Record", record.name)
        doc.delete()

@frappe.whitelist(methods=["GET"])
def get_assets():
        """
        Get all assets from the database.
        """
        data = []
        # Get all assets from the database
        get_result = frappe.db.get_all("Asset", fields=["name", "nomeativo"])
        data.extend([{"name": l["name"], "osiris": l["nomeativo"]} for l in get_result])

        # Get all assets osiris from the database
        get_result = frappe.db.get_all("Asset Config Kartado", fields=["parent", "descricao"])
        data.extend([{"name": l["parent"], "osiris": l["descricao"]} for l in get_result])

        return data

@frappe.whitelist(methods=["GET"])
def get_work_roles():
        """
        Get all work roles from the database.
        """
        data = []
        # Get all assets from the database
        get_result = frappe.db.get_all("Work Role", fields=["name", "funcao"])
        data.extend([{"name": l["name"], "osiris": l["funcao"]} for l in get_result])

        # Get all assets osiris from the database
        get_result = frappe.db.get_all("Work Role Config Kartado", fields=["parent", "descricaokartado"])
        data.extend([{"name": l["parent"], "osiris": l["descricaokartado"]} for l in get_result])

        return data   

@frappe.whitelist(methods=["GET"])
def get_keys(contract_name: str, contract_processing_date: str):
        """
        Get all keys for contract and osiris.
        """
        # Get all contract items from the database
        get_result = frappe.db.get_all("Integration Record", fields=["name"], filters={
             "contrato": contract_name,
             "data": contract_processing_date
        })
        if get_result:
            # If keys found, return the first one
            get_result = frappe.db.get_all("Integration Record Keys", fields=["uuid"], filters={"parent": get_result[0].name})
            return [l.uuid for l in get_result]

        return []

@frappe.whitelist(methods=["GET"])
def get_contract(contract: str, osiris_uuid: str):
        """
        Get contract name for osiris UUID.
        """
        # Get all contract items from the database
        get_result = frappe.db.get_all("Contract", fields=["name", "uuidosiris"], filters={"uuidosiris": osiris_uuid})

        if not get_result:
            # If no contract found with the osiris UUID, check for the contract name
            get_result = frappe.db.get_all("Contract", fields=["name", "uuidosiris"], filters={"contrato": contract})
        
        if not get_result:
            # If no contract found with the contract name, return an empty dictionary
            return {}

        return {"name": get_result[0].name, "osiris": get_result[0].uuidosiris} if get_result else {}

@frappe.whitelist(methods=["GET"])
def get_contract_items(contract_name: str):
        """
        Get all contract items from the database.
        """
        data = []
        # Get all contract items from the database
        get_result = frappe.db.get_all(
            "Contract Item", 
            fields=[
                "name", 
                "codigo", 
                "cidade",
                "dom_hora",
                "seg_hora",
                "ter_hora",
                "qua_hora", 
                "qui_hora",
                "sex_hora",
                "sab_hora",
                "percentualhe"], 
            filters={"contrato": contract_name})
        data.extend(
            [
                {
                    "name": l["name"], 
                    "osiris": l["codigo"], 
                    "cidade": l["cidade"],
                    "dom_hora": l["dom_hora"],
                    "seg_hora": l["seg_hora"],
                    "ter_hora": l["ter_hora"],
                    "qua_hora": l["qua_hora"],
                    "qui_hora": l["qui_hora"],
                    "sex_hora": l["sex_hora"],
                    "sab_hora": l["sab_hora"],
                    "percentualhe": l["percentualhe"]
                 } for l in get_result
            ])

        # Get all contract items osiris from the database
        for l in get_result:
            # Get osiris for each contract item
            get_sub_result = frappe.db.get_all("Contract Item Config Kartado", fields=["codigo"], filters={"parent": l["name"]})
            if get_sub_result:
                data.extend([{"name": l["name"], "osiris": s["codigo"]} for s in get_sub_result])

        return data

@frappe.whitelist(methods=["POST"])
def update_contract(contract: str, osiris_uuid: str):
        """
        Update contract with osiris UUID.
        """
        # Get all contract items from the database
        get_result = frappe.db.get_all("Contract", fields=["name"], filters={"name": contract})
        set_result = frappe.db.set_value("Contract", get_result[0].name, "uuidosiris", osiris_uuid)
        return set_result

@frappe.whitelist(methods=["POST"])
def update_measurements_main_item():

    # Get all Contract Measurement Record
    m_records = frappe.db.get_all("Contract Measurement Record", fields=["name"], filters={"item": ""})
    # m_records = frappe.db.get_all("Contract Measurement Record", fields=["name"])

    for m_record in m_records:
        item_codes = ""
        # Get the measurement record document
        measurement_record = frappe.get_doc("Contract Measurement Record", m_record.name)

        # Get all items from the measurement record
        items = []
        for asset in measurement_record.tabasset:
            if not asset.item in items:
                items.append(asset.item)
        for work_role in measurement_record.tabworkrole:
            if not work_role.item in items:
                items.append(work_role.item)
        for resource in measurement_record.tabrecurso:
            if not resource.item in items:
                items.append(resource.item)

        if items:
            item_codes = get_items_code(items)
            frappe.db.set_value("Contract Measurement Record", m_record.name, "item", item_codes)

    return {"Processed": True, "message": "Measurement records updated with main item."}

@frappe.whitelist(methods=["POST"])
def create_osiris_measurement_record(
    contract_name = None,
    contract_meaesurement = None,
    contract_meaesurement_current = None,
    contract_processing_date = None,
    data = None,
    relations = None):
    """
    Create a osiris Measurement Record.
    """

    if not contract_name:
        # get body data and relations from the request
        # record_type = frappe.form_dict.type
        body = frappe.form_dict
        contract_name = frappe.form_dict.contract_name
        contract_meaesurement = frappe.form_dict.contract_meaesurement
        contract_meaesurement_current = frappe.form_dict.contract_meaesurement_current
        contract_processing_date = frappe.form_dict.contract_processing_date
        data = frappe.form_dict.data
        relations = frappe.form_dict.relations

    def get_date_from_string(data_str: str, year: int = 0, month: int =1, day: int = 2) -> date:
        """
        Convert a date string to a date object.
        :param date_str: The date string in the format 'YYYY-MM-DD'.
        :return: A date object.
        """
        data_str = data_str.split('-')
        year = int(data_str[year])
        month = int(data_str[month]) 
        day = int(data_str[day][:2])   
        new_date = date(year, month, day)
        return new_date    

    def check_osiris_relation(osiris_description, r_type):
        """
        Check ralation between osiris description and osiris list.
        :param osiris: The description of the osiris.
        :param type: The type of relation to check (e.g., "asset", "work_role", "contract_item").
        :return: The name of the osiris relation if found, otherwise None.
        """
        for k in relations[r_type]:
            if k['osiris'] == osiris_description:
                return k["name"]

        return None
    
    def get_week_day(date: date):
        """
        Get the name of the week day.
        :param date: The date object.
        :return: The name of the week day.
        """
        dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
        return dias_semana[date.weekday()]
    
    # List to store inconsistent data
    inconsistent_data = []
    inconsistent_keys = []

    # List of osiris uuids
    osiris_uuids = []
    items = []

    # Measurement Record header
    osiris_measurement_record = None

    # RDO record check
    osiris_key_check = None

    has_itens = False

    # Parse the itens
    for d in data:

        # Check change in RDO or Reporting record
        if d.get('chave',''):
            key_check = f"{d.get('chave','')}"
        else:
            key_check = ""

        if osiris_key_check != key_check:
            if osiris_measurement_record and has_itens:
                # Save the measurement record
                if items:
                    osiris_measurement_record.item = get_items_code(items)                
                # Save the previous measurement record
                osiris_measurement_record.save()

            # Reset the osiris_key_check
            if d.get('chave',''):
                osiris_key_check = f"{d.get('chave','')}"    

            # Reset the osiris_measurement_record
            has_itens = False
            osiris_measurement_record = None
            items = []

        if not osiris_measurement_record:
            date_process = get_date_from_string(d["datacriacao"])
            # Measurement Record header
            osiris_measurement_record = frappe.new_doc("Contract Measurement Record")
            osiris_measurement_record.tipo = f"Osiris - Importação de registros de medição - {d['contrato']}"
            osiris_measurement_record.datacriacao = d["datacriacao"]
            osiris_measurement_record.dataexecucao = d["datacriacao"]
            osiris_measurement_record.dataaprovacao = d["datacriacao"]
            osiris_measurement_record.contrato = contract_name
            osiris_measurement_record.boletimmedicao = contract_meaesurement
            osiris_measurement_record.kminicial = 0
            osiris_measurement_record.kmfinal = 0
            osiris_measurement_record.medicaovigente = contract_meaesurement_current
            osiris_measurement_record.aprovador = d["aprovador"]
            osiris_measurement_record.eh_feriado = False
            osiris_measurement_record.origem_integracao = "Osiris"
            osiris_measurement_record.codigo =d["codigo"]
            osiris_measurement_record.equipe = d["equipe"]
            osiris_measurement_record.length = d["length"]
            osiris_measurement_record.width = d["width"]
            osiris_measurement_record.thickness = d["thickness"]
            osiris_measurement_record.cidade = d["cidade"]
            osiris_measurement_record.entitysystem = d["entitysystem"]
            osiris_measurement_record.rodovia = d["rodovia"]
            osiris_measurement_record.relatorio =  d["codigorelatorio"]
            osiris_measurement_record.diasemana = get_week_day(date_process)

        has_log = False
        # Check log record exists
        for l in osiris_measurement_record.tablog:
            if (l.codigorelatorio == d["codigorelatorio"] and 
                l.dataexecucao == d["dataexecucao"] and 
                l.rodovia == d["rodovia"] and 
                l.via == d["via"] and 
                l.sentido == d["sentido"] and 
                l.faixa == d["faixa"] and 
                l.kminicial == d["kminicial"] and 
                l.kmfinal == d["kmfinal"] and 
                l.observacoes == f"OS: {d['os']}"):
                # Log record already exists, skip
                has_log = True
                break
        # If log record does not exist, create it
        if not has_log:
            osiris_measurement_log_record = osiris_measurement_record.append("tablog")
            osiris_measurement_log_record.codigorelatorio = d["codigorelatorio"]
            osiris_measurement_log_record.dataexecucao = d["dataexecucao"]
            osiris_measurement_log_record.rodovia = d["rodovia"]
            osiris_measurement_log_record.via = d["via"]
            osiris_measurement_log_record.sentido = d["sentido"]
            osiris_measurement_log_record.faixa = d["faixa"]
            osiris_measurement_log_record.kminicial = d["kminicial"]
            osiris_measurement_log_record.kmfinal = d["kmfinal"]
            osiris_measurement_log_record.latitude = None
            osiris_measurement_log_record.longitude = None
            osiris_measurement_log_record.observacoes = f"OS: {d['os']}"     

        has_inconsistent_data = False

        # Check if the osiris relation exists for asset, work role, and contract item
        d["chave_recurso"] = check_osiris_relation(d.get("compositioncode"), "contract_item")

        # Allways check if the item contract relation exists
        if not d["chave_recurso"]:
            msg = f"Relação com item do contrato '{d.get('compositioncode')}' não localizada."
            if msg not in inconsistent_data:
                inconsistent_data.append(msg)
            has_inconsistent_data = True

        if has_inconsistent_data:
            # Add the osiris uuid to the inconsistent keys
            if d["id"] not in inconsistent_keys:
                inconsistent_keys.append(d["id"])
        else:

            if d["chave_recurso"]:
                # Prevent duplicate osiris uuids
                if not d["id"] in osiris_uuids:
                    osiris_uuids.append(d["id"])
                    has_itens = True
                    osiris_measurement_reseource_record = osiris_measurement_record.append("tabrecurso")
                    osiris_measurement_reseource_record.item = d["chave_recurso"]
                    osiris_measurement_reseource_record.quantidademedida = d["itemquantity"]
                    osiris_measurement_reseource_record.valortotal = d["totalvalue"]
                    osiris_measurement_reseource_record.tipo = None
                    osiris_measurement_reseource_record.peso = None
                    osiris_measurement_reseource_record.valorcalculado = d["totalvalue"]
                    if not d["chave_recurso"] in items:
                        items.append(d["chave_recurso"])

    if has_itens:
        # Save the measurement record
        if items:
            osiris_measurement_record.item = get_items_code(items)
        osiris_measurement_record.save()

    # Add the osiris uuids 
    if osiris_uuids:
        integration_record = frappe.new_doc("Integration Record")
        integration_record.contrato = contract_name
        integration_record.data = contract_processing_date
        integration_record.boletimmedicao = contract_meaesurement
        integration_record.tipo = "Osiris"
        for osiris_uuid in osiris_uuids:
            integration_record_key = integration_record.append("tabchaves")
            integration_record_key.uuid = osiris_uuid
        integration_record.save()   

    # Write inconsistent data to the database
    if inconsistent_data:
        s_inconsistency = ""
        s_inconsistency += f"Inconsistências:\n"
        for data in inconsistent_data:
            s_inconsistency += f"{data}\n"

        s_inconsistency += f"Chaves:\n"
        for key in inconsistent_keys:
             s_inconsistency += f"{key}\n"

        # Create a osiris Inconsistency record
        osiris_inconsistent = frappe.new_doc("Integration Inconsistency")
        osiris_inconsistent.boletimmedicao = contract_meaesurement
        osiris_inconsistent.tipo = "Osiris"
        osiris_inconsistent.dataehora = frappe.utils.now()
        osiris_inconsistent.observacoes = s_inconsistency
        osiris_inconsistent.save()

    if has_itens:
        return {
            "message": "Osiris Measurement Record created successfully.",
            "inconsistent_data": inconsistent_data
        }
    else:
        return {
            "message": "No valid osiris items found to create a measurement record.",
            "inconsistent_data": inconsistent_data
        }

def get_items_code(items: list):
    """
    Get all contract items codes.
    """
    get_code = ""
    # Get all contract items from the database
    for i in items:
        # Get osiris for each contract item
        get_code += frappe.db.get_value("Contract Item", i, "codigo") + ", "

    return get_code.rstrip(", ")