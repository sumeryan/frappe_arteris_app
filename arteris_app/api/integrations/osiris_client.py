# import frappe
# import requests
# from datetime import datetime, date, time, timedelta
# from ..osiris import create_osiris_measurement_record, get_keys, get_contract, update_contract, get_contract_items, get_assets, get_work_roles
# from ..measurement import create_measurement

# class OsirisClient():

#     def __init__(self, start_date: datetime, end_date: datetime = datetime.now()):
#         """
#         Initializes the OsirisClient with a start and optional end date for data retrieval.
        
#         Args:
#             start_date (datetime): The start date for the data retrieval.
#             end_date (datetime, optional): The end date for the data retrieval. Defaults to now.
#         """

#         osiris_config = frappe.get_doc("Osiris Config")

#         self.base_url = osiris_config.base_url
#         self.user = osiris_config.user
#         self.password = osiris_config.password

#         self.start_date = start_date
#         self.end_date = end_date

#     def login(self):
#         base_url = self.base_url
#         # Endpoint de login
#         login_url = f"{base_url}/user/login"
#         # Parâmetros de login
#         params = {
#             "Email": self.user,
#             "Password": self.password
#         }
#         # Faz a requisição de login
#         response = requests.get(login_url, params=params)
#         if response.status_code == 200:
#             # O sistema retorna um cookie de sessão - usar o nome correto do cookie
#             session_cookie = response.cookies.get('.Elleve_Rodovias')
#             if not session_cookie:
#                 # Fallback: pegar qualquer cookie disponível
#                 print("Cookies disponíveis:", response.cookies)
#                 # Ou retornar todos os cookies para usar diretamente
#                 self.cookies = response.cookies
#             self.cookies = session_cookie
#         else:
#             raise Exception(f"Falha na autenticação: {response.status_code} - {response.text}")
        
#     def get_producoes(
#             self,
#             page_number=1, 
#             page_size=1000, 
#             start_date=None, 
#             end_date=None):
#         # Endpoint de produções
#         producoes_url = f"{self.base_url}/production/producoes"
#         # Parâmetros de consulta
#         params = {
#             "PageNumber": page_number,
#             "PageSize": page_size
#         }
#         # Adiciona filtros opcionais
#         if start_date:
#             params["DataInicio"] = start_date
#         if end_date:
#             params["DataFim"] = end_date
        
#         # Verifica se session_cookie é um objeto cookies ou uma string
#         if isinstance(self.cookies, requests.cookies.RequestsCookieJar):
#             # Usa o objeto cookies diretamente
#             response = requests.get(producoes_url, params=params, cookies=self.cookies)
#         else:
#             # Headers com o cookie de sessão (formato string)
#             headers = {
#                 "Cookie": f".Elleve_Rodovias={self.cookies}"
#             }
#             response = requests.get(producoes_url, params=params, headers=headers)
        
#         if response.status_code == 200:
#             return response.json()
#         else:
#             raise Exception(f"Erro ao buscar produções: {response.status_code} - {response.text}")

#     # Versão alternativa usando Session para manter cookies automaticamente
#     def create_session_and_login(self):
#         """Cria uma sessão e faz login, mantendo cookies automaticamente"""
#         session = requests.Session()
#         login_url = f"{self.base_url}/user/login"
        
#         params = {
#             "Email": self.user,
#             "Password": self.password
#         }
        
#         response = session.get(login_url, params=params)
#         if response.status_code == 200:
#             self.session = session
#         else:
#             raise Exception(f"Falha na autenticação: {response.status_code} - {response.text}")

#     def get_prod_with_session(
#             self,
#             page_number=1, 
#             page_size=1000, 
#             start_date=None, 
#             end_date=None):
#         """Versão que usa Session object"""
#         producoes_url = f"{self.base_url}/production/producoes"
#         params = {
#             "PageNumber": page_number,
#             "PageSize": page_size
#         }
        
#         if start_date:
#             params["DataInicio"] = start_date
#         if end_date:
#             params["DataFim"] = end_date
        
#         response = self.session.get(producoes_url, params=params)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             raise Exception(f"Erro ao buscar produções: {response.status_code} - {response.text}")

#     def create_osiris_measurement_records(self):

#         # Send data to frappe
#         def write_measurement_record(measurement_records, contract):

#             if not measurement_records:
#                 return None

#             # Write measurement record
#             measurement_record = create_osiris_measurement_record(
#                 contract_name = contract["name"],
#                 contract_meaesurement = contract["measurements"][-1]["name"],
#                 contract_meaesurement_current = contract["measurements"][-1]["current"],
#                 contract_processing_date = contract["processing_date"],
#                 data = measurement_records,
#                 relations = {
#                     "asset": osiris_assets,
#                     "work_role": osiris_work_roles,
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

#         def get_osiris_keys(contract_name, contract_processing_date):
#             """
#             Get Osiris keys for a given contract measurement.
#             """
#             return get_keys(
#                 contract_name=contract_name,
#                 contract_processing_date=contract_processing_date
#             )

#         def load_osiris_data(self):
#             contracts ={}
#             search_date = self.start_date

#             # While loop to iterate through each day
#             while search_date <= self.end_date:

#                 print(f"Search records for day: {search_date.strftime('%Y-%m-%d')}\n")

#                 # Query data from API
#                 self.create_session_and_login()
#                 productions = self.get_prod_with_session(
#                     page_number=1, 
#                     page_size=1000,
#                     data_inicio=search_date.strftime('%Y-%m-%d'), 
#                     data_fim=search_date.strftime('%Y-%m-%d'))
                
#                 print(f"Produções encontradas: {len(productions['Data'])}")

#                 last_contract = ""
#                 measurement_records = []

#                 for p in productions['Data']:

#                     # Ignore if is null
#                     if p['MeasurementInfo']:
                            
#                         rodovia = p['ConcessionaireRoadState']['RoadName']
#                         rodovia = f'{rodovia.upper()}-{p['ConcessionaireRoadState']['StateUf']}'

#                         mcount = 0

#                         for m in p['MeasurementInfo']:

#                             mcount +=1
                            
#                             # Check IsMeasured
#                             if not m['IsMeasured']:
#                                 continue

#                             # Get contract 
#                             osiris_cw = m['Contract']['Number']
#                             osiris_cw_id = m['Contract']['Id']

#                             # Limitar ao contrato CW37273
#                             if not osiris_cw == "CW37273":
#                                 continue

#                             if not osiris_cw in contracts:
#                                 # Get contract name
#                                 contract = { 
#                                     "name": "",
#                                     "code": "",
#                                     "osiris": "",
#                                     "last_measurement_date": None,
#                                     "processing_date": None,
#                                     "process": True,
#                                     "itens": [],
#                                     "keys": [],
#                                     "measurements":[]
#                                 }
#                                 contracts[osiris_cw] = contract
                                
#                                 # Get contract
#                                 data_contract = get_contract(
#                                     contract=osiris_cw,
#                                     osiris_uuid=osiris_cw_id
#                                 )

#                                 if data_contract:
#                                     # Check contract relationship
#                                     if not data_contract["osiris"]:
#                                         # Write relationship to osiris
#                                         update_contract(
#                                             contract=data_contract["name"],
#                                             osiris_uuid=osiris_cw_id
#                                         )

#                                     # Update contract information
#                                     contract["name"] = data_contract["name"]
#                                     contract["osiris"] = osiris_cw_id
#                                     contract["code"] = osiris_cw

#                                     # Get contract items
#                                     itens = get_contract_items(
#                                         contract_name=contract["name"]
#                                     )
#                                     contract["itens"].extend(itens)
#                                 else:
#                                     print(f"Contract not found for {osiris_cw}")
#                                     # Fail on get contract
#                                     contract["process"] = False

#                             else:
#                                 contract = contracts[osiris_cw]

#                             # Set processing date
#                             s_search_date = p['DateProduction'][0:10]
#                             if not contract["processing_date"] == s_search_date:
#                                 contract["processing_date"] = s_search_date
#                                 contract["keys"] = get_osiris_keys(contract["name"], s_search_date)

#                             # Continue only if the contract has a name
#                             if contract["name"] and contract["process"]:

#                                 # Check current measurement for contract
#                                 if not contract["measurements"]:
#                                     measurement = create_new_measurement(search_date, contract)

#                                     # Check if the response contains data
#                                     if measurement and "measurements" in measurement and measurement["measurements"]:
#                                         contract["measurements"].extend(measurement["measurements"])
#                                         contract["last_measurement_date"] = measurement["measurements"][0]["end"]
                                        
#                                     else:
#                                         # Fail on get current measurement
#                                         contract["process"] = False                    

#                             if contract["process"]:                

#                                 # If date is greater than last measurement date, create a new measurement
#                                 if search_date>datetime.strptime(contract["last_measurement_date"], "%Y-%m-%d"):
#                                     measurement = create_new_measurement(search_date, contract)
#                                     contract["measurements"].extend(measurement["measurements"])
#                                     contract["last_measurement_date"] = measurement["measurements"][0]["end"]    

#                                 # Need composition Id to create the key
#                                 id = f"P{mcount:03d}-ID{p['Id']:07d}-ITEM{m['Contract']['ItemComposition']['Id']:07d}"
#                                 key = f"{contract['name']}-{p['Rdo']['Code']}"

#                                 # Add the record to the measurement records
#                                 if id in contract["keys"]:
#                                     continue                                

#                                 measurement_records.append({
#                                     "id": id,
#                                     "chave": key,
#                                     "tipo": 'Osiris',
#                                     "datacriacao": p['DateProduction'],
#                                     "dataexecucao": p['DateProduction'],
#                                     "dataaprovacao": None,
#                                     "contrato": contract["name"],
#                                     "boletimmedicao": contract["measurements"][-1]["name"],
#                                     "kminicial": p['KmStart'],
#                                     "kmfinal": p['KmEnd'],
#                                     "medicaovigente": contract["measurements"][-1]["current"],
#                                     "aprovador": None,
#                                     "eh_feriado": False,
#                                     "mstart": p['Mstart'],
#                                     "mend": p['Mend'],
#                                     "length": p['Length'],
#                                     "width": p['Width'],
#                                     "thickness": p['Thickness'],
#                                     "codigo": p['Rdo']['Code'],
#                                     "cidade": p['City']['Description'],
#                                     "entitysystem": p['EntitySystem']['Description'],
#                                     "atvidade": p['Activity']['Description'][0:120],
#                                     "servico": p['Service']['Description'][0:120],
#                                     "os": p['ServiceOrder']['Code'],
#                                     "contractor": p['Contractor']['FantasyName'],
#                                     "equipe": p['Team']['Description'],
#                                     "laboratorystatus": p['ProductionLaboratoryStatus']['Description'],
#                                     "codigorelatorio": p['Rdo']['Code'],
#                                     "dataexecucao": p['DateProduction'],
#                                     "rodovia": rodovia,
#                                     "via": p['Track']['Description'],
#                                     "sentido": p['Direction']['Description'],
#                                     "faixa": p['Lane']['Description'],
#                                     "kminicial": p['KmStart'],
#                                     "kmfinal": p['KmEnd'],
#                                     "ismeasured": m['IsMeasured'],
#                                     "itemcode": m['Contract']['Item']['CodeItemContract'],
#                                     "itemdescription": m['Contract']['Item']['DescriptionItemContract'],
#                                     "itemunit": m['Contract']['Item']['Unit'],
#                                     "itemquantity": m['Contract']['Item']['Quantity'],
#                                     "compositioncode": m['Contract']['ItemComposition']['Code'],
#                                     "compositiondescription": m['Contract']['ItemComposition']['Description'],
#                                     "compositionunit": m['Contract']['ItemComposition']['Unit'],
#                                     "percentpendingpayment": m['PercentPendingPayment'],
#                                     "quantity": m['Quantity'],
#                                     "unitaryvalue": m['UnitaryValue'],
#                                     "totalvalue": m['TotalValue']
#                                 })

#                 # Next day
#                 search_date += timedelta(days=1)
                
#                 # Write the last measurement record
#                 if measurement_records:
#                     write_measurement_record(measurement_records, contract)

#         # Assets
#         osiris_assets = get_assets()

#         # Work Roles
#         osiris_work_roles = get_work_roles()

#         load_osiris_data()