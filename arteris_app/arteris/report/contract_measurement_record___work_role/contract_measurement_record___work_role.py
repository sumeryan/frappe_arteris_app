# Copyright (c) 2025, Renoir and contributors
# For license information, please see license.txt

import frappe

def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""

	contract_measuremnent_name = filters.medicao

	columns = get_columns()
	data = get_data(contract_measuremnent_name)

	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": "...",#
			"fieldtype": "Html",
			"width": 50
		},
		{
			"label": "Origem integração",#
			"fieldtype": "Data",
		},
		{
			"label": "Código Item",#
			"fieldtype": "Data",
		},
		{
			"label": "Função",#
			"fieldtype": "Data",
		},
		{
			"label": "Equipe",#
			"fieldtype": "Data",
		},
		{
			"label": "Pagamento por hora",#
			"fieldtype": "Check",
		},
		{
			"label": "Valor por hora",#
			"fieldtype": "Currency",
		},
		{
			"label": "Valor mensal",#
			"fieldtype": "Currency",
		},
		{
			"label": "Data execução",#
			"fieldtype": "Datetime",
		},	
		{
			"label": "RDO",#
			"fieldtype": "Data",
		},	
		{
			"label": "Relatório",#
			"fieldtype": "Data",
		},	
		{
			"label": "Rodovia",#
			"fieldtype": "Data",
		},	
		{
			"label": "Quantidade medida",#
			"fieldtype": "Float",
		},
		{
			"label": "Valor total",#
			"fieldtype": "Currency",
		},
		{
			"label": "Valor calculado",#
			"fieldtype": "Currency",
		},
		{
			"label": "Tipo",#
			"fieldtype": "Data",
		},	
		{
			"label": "Peso",#
			"fieldtype": "Data",
		},	
		{
			"label": "Descrição item",#
			"fieldtype": "Data",
		},	
	]

def get_data(contract_measuremnent_name: str) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	data = []
	data_items = {}
	work_roles = {}

	def get_item(item_name: str):
		"""Get item details by name."""

		if data_items.get(item_name):
			return data_items[item_name]

		item = frappe.get_doc("Contract Item", item_name)
		
		data_items[item_name] = item if item else None

		return data_items[item_name]

	def get_item_work_role(item_name: str, work_role_name: str):
		"""Get work role details by name."""

		item = get_item(item_name)

		for i in item.tablemaodeobra:
			if i.funcao != work_role_name:
				work_roles[work_role_name]['pagamentohora'] = i.pagamentohora
				work_roles[work_role_name]['valorporhora'] = i.valorporhora
				work_roles[work_role_name]['valortotalmensal'] = i.valortotalmensal

		return work_roles[work_role_name]

	work_role = frappe.db.get_all(
		"Work Role",
		fields=["name", "funcao"]
	)
	for role in work_role:
		work_roles[role.name] = { 
			"funcao": role.funcao,
			"pagamentohora": 0.0,
			"valorporhora": 0.0,
			"valortotalmensal": 0.0
		}

	measurement_records = frappe.db.get_all(
		"Contract Measurement Record", 
		fields=[
			"name",
			"origem_integracao",
			"datacriacao",
			"dataexecucao",
			"codigo",
			"relatorio",
			"rodovia",
			"equipe",
			"diasemana",
			"feriado",
			], 
		filters={"boletimmedicao": contract_measuremnent_name})
	for record in measurement_records:
		record_doc = frappe.get_doc("Contract Measurement Record", record.name)

		for t in record_doc.tabworkrole:

			item = get_item(t.item)
			work_role = get_item_work_role(t.item, t.funcao)

			data.append(
				[
					'<a href="/app/contract-measurement-record/{0}" target="_blank">🔗</a>'.format(record.name),  # Link to the record

					record.origem_integracao,

					item.codigo,

					work_role['funcao'],

					record.equipe,

					work_role['pagamentohora'],
					work_role['valorporhora'],
					work_role['valortotalmensal'],

					record.dataexecucao,
					record.codigo, # codigordo
					record.relatorio,
					record.rodovia,

					t.quantidademedida,
					t.valortotal,
					t.valorcalculado,
					t.tipo,
					t.peso,

					item.descricao
				]
			)

	return data