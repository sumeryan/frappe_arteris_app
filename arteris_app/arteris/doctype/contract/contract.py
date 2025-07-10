# Copyright (c) 2025, Renoir and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from arteris_app.api.contractitem import create_item_main


class Contract(Document):
	def after_insert(self):
		# This method is called after the document is inserted into the database
		# You can add any custom logic here that needs to run after the contract is created

		# Create the main item for the contract
		create_item_main(self.name)
