# Copyright (c) 2025, Renoir and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint, flt
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""

	contract_measuremnent_name = filters.medicaoß

	columns = get_columns()
	data = get_data(contract_measuremnent_name)

	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": _("Column 1"),
			"fieldname": "column_1",
			"fieldtype": "Data",
		},
		{
			"label": _("Column 2"),
			"fieldname": "column_2",
			"fieldtype": "Int",
		},
	]


def get_data(contract_measuremnent_name: str) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""

	records = []
	data = []
	data_items = {}

	def get_item(item_name: str):
		"""Get item details by name."""

		if data_items.get(item_name):
			return data_items[item_name]

		item = frappe.get_doc("Contract Item", item_name)
		
		data_items[item_name] = item if item else None

		return data_items[item_name]

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
			"equipe"], 
		filters={"boletimmedicao": contract_measuremnent_name, "medicaovigente": "Sim"})
	for record in measurement_records:
		record_doc = frappe.get_doc("Contract Measurement Record", record.name)

		for t in record_doc.time


	


	return [
		["Row 1", 1],
		["Row 2", 2],
	]
