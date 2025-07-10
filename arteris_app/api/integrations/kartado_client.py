# import frappe
# from datetime import datetime, date, time, timedelta
# from .athena.queries import query_data
# from ..kartado import create_kartado_measurement_record, get_keys, get_contract, update_contract, get_contract_items, get_assets, get_work_roles
# from ..measurement import create_measurement

# class KartadoClient():

#     def __init__(self, start_date: datetime, end_date: datetime = datetime.now()):
#         """
#         Initialize the Kartado Athena Client with a date range.
        
#         Args:
#             start_date (datetime): The start date for the data retrieval.
#             end_date (datetime, optional): The end date for the data retrieval. Defaults to now.
#         """
#         self.start_date = start_date
#         self.end_date = end_date
    
#     def get_measurement_records(self):

#         # Send data to frappe
#         def write_measurement_record(measurement_records, contract):

#             if not measurement_records:
#                 return None

#             measurement_record = create_kartado_measurement_record(
#                 contract_name=contract["name"],
#                 contract_meaesurement=contract["measurements"][-1]["name"],
#                 contract_meaesurement_current=contract["measurements"][-1]["current"],
#                 contract_processing_date=contract["processing_date"],
#                 data=measurement_records,
#                 relations={
#                     "asset": kartado_assets,
#                     "work_role": kartado_work_roles,
#                     "contract_item": contract["itens"]
#                 }
#             )

#             return measurement_record

#         # Create or return contract measurements
#         def create_new_measurement(search_date: datetime, contract):
    
#             # Create or return contract measurements
#             month = search_date.strftime("%m")
#             year = search_date.strftime("%Y")

#             return create_measurement(
#                 month=month,
#                 year=year,
#                 ignore_current_measurement=True,
#                 contract=contract['name']
#             )

#         def get_kartado_keys(contract_name, contract_processing_date):
#             """
#             Get kartado keys for a given contract measurement.
#             """
#             return get_keys(
#                 contract_name=contract_name,
#                 contract_processing_date=contract_processing_date
#             )

#         def load_kartado_data():
#             """
#             Get kartado data for a given type.
#             args:
#                 record_type (str): The type of kartado data to retrieve (e.g., 'adm', 'non_adm', 'rdo').
#             """

#             contracts_to_process = frappe.db.get_list(
#                 "Contract",
#                 fields=["name"],
#                 filters={
#                     "datainiciomedicao": ["<=", self.start_date],
#                     "contratoencerrado": ["is", "not set"]
#                     }
#             )
        
#             if not contracts_to_process:
#                 print("No contracts to process.")
#                 return

#             str_contracts_to_process = ', '.join([f"'{c['name']}'" for c in contracts_to_process])

#             # Contracts
#             contracts ={}
#             search_date = self.start_date
#             counter = 0

#             # Type RDO
#             str_rdo_where = "not u.rdo_id is null and "
#             str_rdo_from = """ inner join prd_gold_data.rdo rdo on rdo.mdruuid = u.rdo_id 
#                             left join prd_gold_data.rdo_reporting_relationship r on r.mdruuid = u.rdo_id 
#                             left join prd_gold_data.apontamentos log on log.uuid_reportings = r.reportinguuid """
        
#             # Type RPT
#             str_rpt_where = "not u.reporting_id is null and u.rdo_id is null and "
#             str_rpt_from = """ left join prd_gold_data.apontamentos log on log.uuid_reportings = u.reporting_id 
#                             left join prd_gold_data.rdo rdo on rdo.mdruuid = null """
            
#             # Type Others
#             str_oth_where = "u.reporting_id is null and u.rdo_id is null and "
#             str_oth_from = """ left join prd_gold_data.apontamentos log on log.uuid_reportings = null 
#                             left join prd_gold_data.rdo rdo on rdo.mdruuid = null """
            
#             str_select = """select
#                                 c.uuid as chave_contrato,
#                                 u.uuid as chave_utilizacao,
#                                 u.item_contratual_id as chave_item_contrato,
#                                 c.numero_objeto as contrato,
#                                 u.data_criacao,
#                                 ic.codigo_item,
#                                 ic.nome  as recurso_item,
#                                 ic.unidade_medida,
#                                 ic.tipo_item,
#                                 ic.peso,
#                                 ic.tipo_administracao,
#                                 u.quantidade,
#                                 u.valor_total,
#                                 u.valor_unitario,
#                                 u.data_aprovacao,
#                                 u.status_aprovacao,
#                                 u.resource_id as chave_recurso,
#                                 u.aprovado_por_nome as aprovado_por,
#                                 log.uuid_reportings as log_chave_relatorio,
#                                 log.number_reportings as log_codigo_relatorio,
#                                 log.executed_at_reportings as log_data_execucao,
#                                 log.created_at_reportings as log_criado_em,
#                                 log.updated_at_reportings as log_atualizado_em,
#                                 log.due_at_reportings as log_data_vencimento,
#                                 log.start_date_work_plan as log_data_inicio_planejamento,
#                                 log.end_date_work_plan as log_data_fim_planejamento,                            
#                                 log.road_name_reportings as log_nome_rodovia,
#                                 log.km_reference_reportings as log_km_referencia,
#                                 log.km_reportings as log_km_inicial,
#                                 log.end_km_reportings as log_km_final,
#                                 log.longitude_reportings as log_longitude,
#                                 log.latitude_reportings as log_latitude,
#                                 log.form_data_reportings as log_notas_formulario,
#                                 log.form_data_reportings as log_notas_formulario_json,
#                                 log.direction_reportings as log_sentido,
#                                 log.lane_reportings as log_pista,                            
#                                 rdo.mdruuid as rdo_chave,
#                                 rdo.number as rdo_serial,
#                                 rdo."date" as rdo_data,
#                                 rdo.createdby as rdo_criado_por,
#                                 rdo.responsible as rdo_responsavel,
#                                 rdo.morningweather as rdo_clima_manha,
#                                 rdo.afternoonweather as rdo_clima_tarde,
#                                 rdo.nightweather as rdo_clima_noite,
#                                 rdo.morningconditions as rdo_condicoes_manha,
#                                 rdo.afternoonconditions as rdo_condicoes_tarde,
#                                 rdo.nightconditions as rdo_condicoes_noite, 
#                                 rdo.firm as rdo_equipe,
#                                 rdo.morningstart as rdo_hora_inicio_manha,
#                                 rdo.morningend as rdo_hora_fim_manha,
#                                 rdo.afternoonstart as rdo_hora_inicio_tarde,
#                                 rdo.afternoonend as rdo_hora_fim_tarde,
#                                 rdo.nightstart as rdo_hora_inicio_noite,
#                                 rdo.nightend as rdo_hora_fim_noite, """
                                
#             str_from = """ from 
#                                 prd_gold_data.itens_contratuais ic 
#                                 inner join prd_gold_data.contratos c on c.uuid = ic.contrato_id
#                                 inner join prd_gold_data.utilizacoes u on ic.uuid = u.item_contratual_id """
            
#             # str_where = """ not c.status_nome = 'Encerrado' and
#             #                 u.status_aprovacao = 'aprovado' and
#             #                 ic.contrato_id = '1f4d09f6-4ae1-411a-bd9a-5a623e926368' and """
#             str_where = f""" not c.status_nome = 'Encerrado' and
#                             u.status_aprovacao = 'aprovado' and
#                             ic.contrato_id IN ({str_contracts_to_process}) and """            
            
#             # While loop to iterate through each day
#             while search_date <= self.end_date:

#                 str_query = f"""{str_select}
#                                     0 as ordem,
#                                     'rdo' as tipo_registro
#                                     {str_from}
#                                     {str_rdo_from}
#                                 where
#                                     {str_rdo_where}
#                                     {str_where}
#                                     CAST(parse_datetime(rdo."date", 'dd-MM-yyyy') AS DATE) between timestamp '{search_date.strftime("%Y-%m-%d")} 00:00:00' and timestamp '{search_date.strftime("%Y-%m-%d")} 23:59:59'
#                                 union all
#                                 {str_select}
#                                     1 as ordem,
#                                     'log' as tipo_registro
#                                     {str_from}
#                                     {str_rpt_from}
#                                 where
#                                     {str_rpt_where}
#                                     {str_where}
#                                     log.executed_at_reportings between timestamp '{search_date.strftime("%Y-%m-%d")} 00:00:00' and timestamp '{search_date.strftime("%Y-%m-%d")} 23:59:59'
#                                 union all
#                                 {str_select}
#                                     2 as ordem,
#                                     'others' as tipo_registro
#                                     {str_from}
#                                     {str_oth_from}
#                                 where
#                                     {str_oth_where}
#                                     {str_where}
#                                     u.data_criacao between timestamp '{search_date.strftime("%Y-%m-%d")} 00:00:00' and timestamp '{search_date.strftime("%Y-%m-%d")} 23:59:59'
#                                 order by 
#                                     ordem,
#                                     rdo_chave,
#                                     log_chave_relatorio,
#                                     chave_contrato;"""      

#                 print(f"Search records for day: {search_date.strftime('%Y-%m-%d')}\n")

#                 # print(str_query.replace("\n", " ").replace("\t", " ").replace("  ", " "))

#                 # Run a simple SELECT query to get the first 10 rows
#                 results = query_data(
#                     query=str_query,
#                     database="prd_gold_data",
#                     output_location=OUTPUT_LOCATION,
#                     region_name=AWS_REGION,
#                     aws_access_key_id=AWS_ACCESS_KEY_ID,
#                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                
#                 last_contract = ""
#                 measurement_records = []

#                 records = results.to_dict('records')

#                 print(f"Records for {search_date.strftime('%Y-%m-%d')}: {len(records)}")

#                 # Check if results are empty
#                 for record in records:
                    
#                     counter += 1
#                     print(f"Processing {search_date.strftime('%Y-%m-%d')} {counter:06d} of {len(records):06d} RDO {record['rdo_chave']}")

#                     # Check if the record is already in the contract's items
#                     if last_contract != record["chave_contrato"]:

#                         # Check it not first record
#                         if last_contract:
#                             write_measurement_record(measurement_records, contract)

#                         # Reset the measurement records for the new contract
#                         measurement_records = []
#                         last_contract = record["chave_contrato"]            

#                     # Check if the record is already in the contracts dictionary
#                     if record["chave_contrato"] not in contracts:
#                         contract = { 
#                             "name": "",
#                             "code": "",
#                             "kartado": "",
#                             "last_measurement_date": None,
#                             "processing_date": None,
#                             "process": True,
#                             "itens": [],
#                             "keys": [],
#                             "measurements":[]
#                         }
#                         contracts[record["chave_contrato"]] = contract
                        
#                         # Get contract
#                         data_contract = get_contract(
#                             contract=record["contrato"],
#                             kartado_uuid=record["chave_contrato"]
#                         )
                        
#                         if data_contract:
#                             # Check contract relationship
#                             if not data_contract["kartado"]:
#                                 # Write relationship to kartado
#                                 update_contract(
#                                     contract=data_contract["name"],
#                                     kartado_uuid=record["chave_contrato"]
#                                 )

#                             # Update contract information
#                             contract["name"] = data_contract["name"]
#                             contract["kartado"] = record["chave_contrato"]
#                             contract["code"] = record["contrato"] 

#                             # Get contract items
#                             itens = get_contract_items(
#                                 contract_name=contract["name"]
#                             )
#                             contract["itens"].extend(itens)
#                         else:
#                             print(f"Contract not found for {record['contrato']}")
#                             # Fail on get contract
#                             contract["process"] = False

#                     else:
#                         contract = contracts[record["chave_contrato"]]
                        
#                     # Set processing date
#                     s_search_date = record["data_criacao"][0:10]
#                     if not contract["processing_date"] == s_search_date:
#                         contract["processing_date"] = s_search_date
#                         contract["keys"] = get_kartado_keys(contract["name"], s_search_date)
            
#                     # Continue only if the contract has a name
#                     if contract["name"] and contract["process"]:

#                         # Check current measurement for contract
#                         if not contract["measurements"]:
#                             measurement = create_new_measurement(search_date, contract)

#                             # Check if the response contains data
#                             if measurement and "measurements" in measurement and measurement["measurements"]:
#                                 contract["measurements"].extend(measurement["measurements"])
#                                 contract["last_measurement_date"] = measurement["measurements"][0]["end"]
                                
#                             else:
#                                 # Fail on get current measurement
#                                 contract["process"] = False

#                     if contract["process"]:                

#                         # If date is greater than last measurement date, create a new measurement
#                         if search_date>datetime.strptime(contract["last_measurement_date"], "%Y-%m-%d"):
#                             measurement = create_new_measurement(search_date, contract)
#                             contract["measurements"].extend(measurement["measurements"])
#                             contract["last_measurement_date"] = measurement["measurements"][0]["end"]    

#                         # Add the record to the measurement records
#                         if not record["chave_utilizacao"] in contract["keys"]:
#                             measurement_records.append(record)

#                 # Next day
#                 search_date += timedelta(days=1)
                
#                 # Write the last measurement record
#                 if measurement_records:
#                     write_measurement_record(measurement_records, contract)

#             # Write the last measurement record
#             if measurement_records:
#                 write_measurement_record(measurement_records, contract)

#         kartado_config = frappe.get_doc("Kartado Config")
        
#         # S3 output location for query results
#         OUTPUT_LOCATION = kartado_config.s3_output_location
#         AWS_REGION = kartado_config.aws_region
#         AWS_ACCESS_KEY_ID = kartado_config.aws_access_key_id
#         AWS_SECRET_ACCESS_KEY = kartado_config.aws_secret_access_key

#         # Assets
#         kartado_assets = get_assets()

#         # Work Roles
#         kartado_work_roles = get_work_roles()

#         # Load kartado data
#         load_kartado_data()
