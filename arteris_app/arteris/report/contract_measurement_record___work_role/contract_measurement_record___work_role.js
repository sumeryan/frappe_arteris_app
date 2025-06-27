// Copyright (c) 2025, Renoir and contributors
// For license information, please see license.txt

frappe.query_reports["Contract Measurement Record - Work Role"] = {
	filters: [
		{
			"fieldname": "medicao",
			"label": "Boletim de medição",
			"fieldtype": "Link",
			"options": "Contract Measurement",
			"reqd": 1
		}
		// {
		// 	"fieldname": "my_filter",
		// 	"label": __("My Filter"),
		// 	"fieldtype": "Data",
		// 	"reqd": 1,
		// },
	],
};
