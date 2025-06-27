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
			"label": "Descrição item",#
			"fieldtype": "Data",
		},
		{
			"label": "Equipe",#
			"fieldtype": "Data",
		},
		{
			"label": "Valor unitário",#
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

	]

def get_data(contract_measuremnent_name: str) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	data = []
	data_items = {}
	resources = {}

	def get_item(item_name: str):
		"""Get item details by name."""

		if data_items.get(item_name):
			return data_items[item_name]

		item = frappe.get_doc("Contract Item", item_name)
		
		data_items[item_name] = item if item else None

		return data_items[item_name]

	def get_item_resource(item_name: str):
		"""Get work role details by name."""

		item = get_item(item_name)

		return item

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

		for t in record_doc.tabrecurso:

			item = get_item(t.item)

			data.append(
				[
					'<a href="/app/contract-measurement-record/{0}" target="_blank">🔗</a>'.format(record.name),  # Link to the record

					record.origem_integracao,

					item.codigo,

					item.descricao,

					record.equipe,

					item.valorunitario,

					record.dataexecucao,
					record.codigo, # codigordo
					record.relatorio,
					record.rodovia,

					t.quantidademedida,
					t.valortotal,
					t.valorcalculado,
					t.tipo,
					t.peso,

				]
			)

	return data