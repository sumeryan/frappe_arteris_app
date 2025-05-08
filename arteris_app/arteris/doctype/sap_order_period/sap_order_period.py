# Copyright (c) 2025, Renoir and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SAPOrderPeriod(Document):
    def autoname(self):
        parent_doc = frappe.get_doc(self.parenttype, self.parent)
        # Use a field from the parent and a child field to create the name
        self.name = f"{parent_doc.numeropedido}-{self.linhapedido}"
