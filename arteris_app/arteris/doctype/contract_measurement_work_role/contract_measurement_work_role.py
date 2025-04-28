# Copyright (c) 2025, Renoir and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ContractMeasurementWorkRole(Document):
	pass

# class ContractMeasurementWorkRole(Document):
#     def validate(self):
#         # Verificar se temos os campos necessários preenchidos
#         if self.item and self.funcao:
#             # Buscar o valor de funcao na tabela filha Contract Item Work Role
#             # filtrando pelo item e funcao do documento atual
#             funcoes_item = frappe.get_all(
#                 "Contract Item Work Role",  # Nome do DocType da tabela filha
#                 filters={
#                     "parent": self.item,       # Item selecionado no documento atual
#                     "funcao": self.funcao      # Função selecionada no documento atual
#                 },
#                 fields=["name"]
#             )
            
#             # Se encontrou algum resultado, atribui ao campo funcaoitem
#             if funcoes_item and len(funcoes_item) > 0:
#                 self.funcaoitem = funcoes_item[0].name