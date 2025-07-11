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

    # str_contracts_to_process = ', '.join([f"'{c}'" for c in contracts_to_process])    

    # return str_contracts_to_process

    return contracts_to_process

@frappe.whitelist(methods=["DELETE"])
def clear_keys():
    """
    Clear all keys from the database.
    """
    get_result = frappe.db.get_all("Integration Record", fields=["name"], filters={"tipo": "Kartado"})
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
        data.extend([{"name": l["name"], "kartado": l["nomeativo"]} for l in get_result])

        # Get all assets kartado from the database
        get_result = frappe.db.get_all("Asset Config Kartado", fields=["parent", "descricao"])
        data.extend([{"name": l["parent"], "kartado": l["descricao"]} for l in get_result])

        return data

@frappe.whitelist(methods=["GET"])
def get_work_roles():
        """
        Get all work roles from the database.
        """
        data = []
        # Get all assets from the database
        get_result = frappe.db.get_all("Work Role", fields=["name", "funcao"])
        data.extend([{"name": l["name"], "kartado": l["funcao"]} for l in get_result])

        # Get all assets kartado from the database
        get_result = frappe.db.get_all("Work Role Config Kartado", fields=["parent", "descricaokartado"])
        data.extend([{"name": l["parent"], "kartado": l["descricaokartado"]} for l in get_result])

        return data   

@frappe.whitelist(methods=["GET"])
def get_keys(contract_name: str, contract_processing_date: str):
        """
        Get all keys for contract and kartado.
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
def get_contract(contract: str, kartado_uuid: str):
        """
        Get contract name for kartado UUID.
        """
        # Get all contract items from the database
        get_result = frappe.db.get_all("Contract", fields=["name", "uuidkartado"], filters={"uuidkartado": kartado_uuid})

        if not get_result:
            # If no contract found with the kartado UUID, check for the contract name
            get_result = frappe.db.get_all("Contract", fields=["name", "uuidkartado"], filters={"contrato": contract})
        
        if not get_result:
            # If no contract found with the contract name, return an empty dictionary
            return {}

        return {"name": get_result[0].name, "kartado": get_result[0].uuidkartado} if get_result else {}

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
                    "kartado": l["codigo"], 
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

        # Get all contract items kartado from the database
        for l in get_result:
            # Get kartado for each contract item
            get_sub_result = frappe.db.get_all("Contract Item Config Kartado", fields=["codigo"], filters={"parent": l["name"]})
            if get_sub_result:
                data.extend([{"name": l["name"], "kartado": s["codigo"]} for s in get_sub_result])

        return data

@frappe.whitelist(methods=["POST"])
def update_contract(contract: str, kartado_uuid: str):
        """
        Update contract with kartado UUID.
        """
        # Get all contract items from the database
        get_result = frappe.db.get_all("Contract", fields=["name"], filters={"contrato": contract})
        set_result = frappe.db.set_value("Contract", get_result[0].name, "uuidkartado", kartado_uuid)
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
def create_kartado_measurement_record(
    contract_name = None,
    contract_meaesurement = None,
    contract_meaesurement_current = None,
    contract_processing_date = None,
    data = None,
    relations = None):
    """
    Create a Kartado Measurement Record.
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

    holidays = {}

    def get_item(item: str) -> dict:
        """
        Get the city of a contract item.
        """
        # Get kartado for each contract item
        for i in relations["contract_item"]:
            if i['name'] == item:
                return i
        return None

    def check_kartado_relation(kartado_description, r_type):
        """
        Check ralation between kartado description and kartado list.
        :param kartado_description: The description of the kartado.
        :param type: The type of relation to check (e.g., "asset", "work_role", "contract_item").
        :return: The name of the kartado relation if found, otherwise None.
        """
        for k in relations[r_type]:
            if k['kartado'] == kartado_description:
                return k["name"]

        return None
    
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

    # List of kartado uuids
    kartado_uuids = []
    kartado_logs = []
    items = []
    str_logs = ""
    str_highways = ""

    # Measurement Record header
    kartado_measurement_record = None

    # RDO record check
    kartado_rdo_check = None

    has_itens = False

    # Parse the itens
    for d in data:

        # Check change in RDO or Reporting record
        if d.get('rdo_chave',''):
            rdo_check = f"{d.get('rdo_chave','')}"
        elif d.get('log_chave_relatorio',''):
            rdo_check = f"{d.get('log_chave_relatorio','')}"
        else:
            rdo_check = ""

        if kartado_rdo_check != rdo_check:
            if kartado_measurement_record and has_itens:
                # Save the previous measurement record
                # Save the measurement record
                if items:
                    kartado_measurement_record.item = get_items_code(items)                
                kartado_measurement_record.relatorio = str_logs[0:30]
                kartado_measurement_record.rodovia = str_highways[0:30]
                kartado_measurement_record.save()

            # Reset the kartado_rdo_check
            if d.get('rdo_chave',''):
                kartado_rdo_check = f"{d.get('rdo_chave','')}"
            elif d.get('log_chave_relatorio',''):
                kartado_rdo_check = f"{d.get('log_chave_relatorio','')}"
            else:
                kartado_rdo_check = ""            

            # Reset the kartado_measurement_record
            has_itens = False
            kartado_measurement_record = None
            kartado_logs = []
            items = []
            str_logs = ""
            str_highways = ""

        if not kartado_measurement_record:
            # Measurement Record header
            kartado_measurement_record = frappe.new_doc("Contract Measurement Record")
            kartado_measurement_record.tipo = f"Kartado - Importação de registros de medição - {d['contrato']}"
            kartado_measurement_record.datacriacao = d["data_criacao"]
            kartado_measurement_record.dataexecucao = d["data_criacao"]
            kartado_measurement_record.dataaprovacao = d["data_aprovacao"]
            kartado_measurement_record.contrato = contract_name
            kartado_measurement_record.boletimmedicao = contract_meaesurement
            kartado_measurement_record.kminicial = 0
            kartado_measurement_record.kmfinal = 0
            kartado_measurement_record.medicaovigente = contract_meaesurement_current
            kartado_measurement_record.aprovador = d["aprovado_por"]
            kartado_measurement_record.eh_feriado = False

            if d["tipo_registro"] == "rdo": # or record_type == "rpt":
                data_execucao = d["rdo_data"].split('-')
                kartado_measurement_record.dataexecucao = f"{data_execucao[2]}-{data_execucao[1]}-{data_execucao[0]}"
                kartado_measurement_record.origem_integracao = "Kartado RDO"
            elif d["tipo_registro"] == "log":
                kartado_measurement_record.dataexecucao = d["log_data_execucao"] 
                kartado_measurement_record.origem_integracao = "Kartado Apontamento"
            else:
                kartado_measurement_record.origem_integracao = "Kartado Outros"

            # Set code using reporting code
            if d["log_codigo_relatorio"]:
                kartado_measurement_record.codigo = d["log_codigo_relatorio"]

            # RDO contains data
            if d["rdo_chave"]:
                kartado_measurement_record.responsavel = d["rdo_responsavel"]
                kartado_measurement_record.codigo = d["rdo_serial"] #d["rdo_chave"]
                kartado_measurement_record.climadamanha = d["rdo_clima_manha"]
                kartado_measurement_record.condicoesdamanha = d["rdo_condicoes_manha"]
                kartado_measurement_record.climadatarde = d["rdo_clima_tarde"]
                kartado_measurement_record.condicoesdatarde = d["rdo_condicoes_tarde"]
                kartado_measurement_record.climadanoite = d["rdo_clima_noite"]
                kartado_measurement_record.condicoesdanoite = d["rdo_condicoes_noite"]
                kartado_measurement_record.criadopor = d["rdo_criado_por"]
                kartado_measurement_record.equipe = d["rdo_equipe"]

        has_inconsistent_data = False

        # Check if the kartado relation exists for asset, work role, and contract item
        d["chave_ativo"] = check_kartado_relation(d.get("recurso_item"), "asset")
        d["chave_funcao"] = check_kartado_relation(d.get("recurso_item"), "work_role")
        d["chave_recurso"] = check_kartado_relation(d.get("codigo_item"), "contract_item")
        record_contract_item = get_item(d["chave_recurso"])
        
        # Check if is administrative record
        if d["tipo_administracao"]:
            if not d["chave_ativo"] and not d["chave_funcao"]:
                msg = f"Relação de ativo ou função '{d.get('recurso_item')}' não localizado."
                if msg not in inconsistent_data:
                    inconsistent_data.append(msg)
                has_inconsistent_data = True

        # Allways check if the item contract relation exists
        if not d["chave_recurso"]:
            msg = f"Relação com item do contrato '{d.get('codigo_item')}' não localizada."
            if msg not in inconsistent_data:
                inconsistent_data.append(msg)
            has_inconsistent_data = True

        if has_inconsistent_data:
            # Add the kartado uuid to the inconsistent keys
            if d["chave_utilizacao"] not in inconsistent_keys:
                inconsistent_keys.append(d["chave_utilizacao"])
        else:
            
            # Create work role measurement record
            if d["chave_funcao"]:
                if not d["chave_utilizacao"] in kartado_uuids:
                    kartado_uuids.append(d["chave_utilizacao"])
                    has_itens = True
                    kartado_measurement_work_role_record = kartado_measurement_record.append("tabworkrole")
                    kartado_measurement_work_role_record.item = d["chave_recurso"]
                    kartado_measurement_work_role_record.funcao = d["chave_funcao"]
                    kartado_measurement_work_role_record.quantidademedida = d["quantidade"]
                    kartado_measurement_work_role_record.valortotal = d["valor_total"]
                    kartado_measurement_work_role_record.valorcalculado = 0.0
                    kartado_measurement_work_role_record.tipo = d["tipo_item"]
                    kartado_measurement_work_role_record.peso = d["peso"]
                    if not d["chave_recurso"] in items:
                        items.append(d["chave_recurso"])

                    if d["tipo_item"] == "administração":
                        # Set the default date to process
                        date_process = get_date_from_string(d["data_criacao"])
                        #Date to process
                        if d["tipo_registro"] == "rdo":
                            date_process = get_date_from_string(d["rdo_data"], 2, 1, 0)
                        if d["tipo_registro"] == "log":
                            date_process = get_date_from_string(d["log_data_execucao"])
                        if d["tipo_registro"] == "others":
                            date_process = get_date_from_string(d["data_criacao"])
                        
                        # Timestamp strings
                        ts_start = "2000-01-01 00:00:00.000"
                        ts_end = "2000-01-01 00:00:00.000"

                        # Get start hour
                        if ts_start == ts_end and d["rdo_hora_inicio_manha"]:
                            ts_start = f'2000-01-01 {d["rdo_hora_inicio_manha"]}:00.000'
                        if ts_start == ts_end and d["rdo_hora_inicio_tarde"]:                            
                            ts_start = f'2000-01-01 {d["rdo_hora_inicio_tarde"]}:00.000'
                        if ts_start == ts_end and d["rdo_hora_inicio_noite"]:                            
                            ts_start = f'2000-01-01 {d["rdo_hora_inicio_noite"]}:00.000'

                        # Get last hour
                        if d["rdo_hora_fim_manha"]:
                            ts_end =  f'2000-01-01 {d["rdo_hora_fim_manha"]}:00.000'
                        if d["rdo_hora_fim_tarde"]:
                            ts_end =  f'2000-01-01 {d["rdo_hora_fim_tarde"]}:00.000'
                        if d["rdo_hora_fim_noite"]:
                            ts_end =  f'2000-01-01 {d["rdo_hora_fim_noite"]}:00.000'

                        # Converter para datetime
                        time_start = datetime.strptime(ts_start, '%Y-%m-%d %H:%M:%S.%f')
                        time_end = datetime.strptime(ts_end, '%Y-%m-%d %H:%M:%S.%f')                        

                        # Hours record
                        kartado_measurement_record_time = kartado_measurement_record.append("tabhoras")
                        kartado_measurement_record_time.item = d["chave_recurso"]
                        kartado_measurement_record_time.funcao = d["chave_funcao"]
                        kartado_measurement_record_time.quantidade = d["quantidade"] # 1
                        kartado_measurement_record_time.horainicial = time_start.strftime('%H:%M:%S')
                        kartado_measurement_record_time.horafinal = time_end.strftime('%H:%M:%S')
                        kartado_measurement_record_time.compensacoes = 0.0
                        kartado_measurement_record_time.horaextra100 = 0.0
                        kartado_measurement_record_time.horaextra = 0.0
                        kartado_measurement_record_time.horanormal = 0.0
                        kartado_measurement_record_time.horanormalda = 0.0
                        kartado_measurement_record_time.valorcalculado = 0.0
                        # Return the name of weekday
                        kartado_measurement_record.diasemana = get_week_day(date_process)

            # Create asset measurement record
            if d["chave_ativo"]:
                if not d["chave_utilizacao"] in kartado_uuids:
                    kartado_uuids.append(d["chave_utilizacao"])
                    has_itens = True
                    kartado_measurement_asset_record = kartado_measurement_record.append("tabasset")
                    kartado_measurement_asset_record.item = d["chave_recurso"]
                    kartado_measurement_asset_record.maquina_equipamento_ou_ferramenta = d["chave_ativo"]
                    kartado_measurement_asset_record.quantidademedida = d["quantidade"]
                    kartado_measurement_asset_record.valortotal = d["valor_total"]
                    kartado_measurement_asset_record.valorcalculado = 0.0
                    kartado_measurement_asset_record.tipo = d["tipo_item"]
                    kartado_measurement_asset_record.peso = d["peso"]                
                    if not d["chave_recurso"] in items:
                        items.append(d["chave_recurso"])

            if not d["chave_ativo"] and not d["chave_funcao"]:
                 if d["chave_recurso"]:
                    # Prevent duplicate kartado uuids
                    if not d["chave_utilizacao"] in kartado_uuids:
                        kartado_uuids.append(d["chave_utilizacao"])
                        has_itens = True
                        kartado_measurement_reseource_record = kartado_measurement_record.append("tabrecurso")
                        kartado_measurement_reseource_record.item = d["chave_recurso"]
                        kartado_measurement_reseource_record.quantidademedida = d["quantidade"]
                        kartado_measurement_reseource_record.valortotal = d["valor_total"]
                        kartado_measurement_reseource_record.tipo = d["tipo_item"]
                        kartado_measurement_reseource_record.peso = d["peso"]      
                        kartado_measurement_reseource_record.valorcalculado = 0.0
                        if not d["chave_recurso"] in items:
                            items.append(d["chave_recurso"])

            if d["log_codigo_relatorio"]:
                if not d["log_codigo_relatorio"] in kartado_logs:
                    kartado_logs.append(d["log_codigo_relatorio"])
                    if not d["chave_utilizacao"] in kartado_uuids:
                        kartado_uuids.append(d["chave_utilizacao"])
                    has_itens = True
                    kartado_measurement_log_record = kartado_measurement_record.append("tablog")
                    kartado_measurement_log_record.codigorelatorio = d["log_codigo_relatorio"]
                    kartado_measurement_log_record.dataexecucao = d["log_data_execucao"]
                    kartado_measurement_log_record.rodovia = d["log_nome_rodovia"]
                    kartado_measurement_log_record.kminicial = d["log_km_inicial"]
                    kartado_measurement_log_record.kmfinal = d["log_km_final"]
                    kartado_measurement_log_record.latitude = d["log_latitude"]
                    kartado_measurement_log_record.longitude = d["log_longitude"]
                    kartado_measurement_log_record.observacoes = d["log_notas_formulario_json"]
                    kartado_measurement_log_record.sentido = d["log_sentido"]
                    kartado_measurement_log_record.faixa = d["log_pista"]
                    if str_logs:
                        str_logs += ", "
                    str_logs += d["log_codigo_relatorio"]
                    if str_highways:
                        str_highways += ", "
                    str_highways += d["log_nome_rodovia"]

    if has_itens:
        # Save the measurement record
        if items:
            kartado_measurement_record.item = get_items_code(items)
        kartado_measurement_record.relatorio = str_logs[0:30]
        kartado_measurement_record.rodovia = str_highways[0:30]
        kartado_measurement_record.save()

    # Add the kartado uuids 
    if kartado_uuids:
        integration_record = frappe.new_doc("Integration Record")
        integration_record.contrato = contract_name
        integration_record.data = contract_processing_date
        integration_record.boletimmedicao = contract_meaesurement
        integration_record.tipo = "Kartado"
        for kartado_uuid in kartado_uuids:
            integration_record_key = integration_record.append("tabchaves")
            integration_record_key.uuid = kartado_uuid
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

        # Create a Kartado Inconsistency record
        kartado_inconsistent = frappe.new_doc("Integration Inconsistency")
        kartado_inconsistent.boletimmedicao = contract_meaesurement
        kartado_inconsistent.tipo = "Kartado"
        kartado_inconsistent.dataehora = frappe.utils.now()
        kartado_inconsistent.observacoes = s_inconsistency
        kartado_inconsistent.save()

    if has_itens:
        return {
            "message": "Kartado Measurement Record created successfully.",
            "inconsistent_data": inconsistent_data
        }
    else:
        return {
            "message": "No valid kartado items found to create a measurement record.",
            "inconsistent_data": inconsistent_data
        }

def get_items_code(items: list):
    """
    Get all contract items codes.
    """
    get_code = ""
    # Get all contract items from the database
    for i in items:
        # Get kartado for each contract item
        get_code += frappe.db.get_value("Contract Item", i, "codigo") + ", "

    return get_code.rstrip(", ")
    

