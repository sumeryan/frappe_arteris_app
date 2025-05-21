# Copyright (c) 2025, Renoir and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe import _


class ContractItemType(Document):
	@property
	def hook_tipovirtual(self):
		return "TESTE"
