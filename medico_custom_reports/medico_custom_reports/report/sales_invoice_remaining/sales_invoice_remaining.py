# Copyright (c) 2025, abdopcnet@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from frappe.utils import flt, getdate

def execute(filters=None):
	return SalesInvoiceRemaining(filters).run()

class SalesInvoiceRemaining:
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		
	def run(self):
		self.get_columns()
		self.get_data()
		return self.columns, self.data
		
	def get_columns(self):
		self.columns = [
			{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer"},
			{"label": _("Sales Invoice"), "fieldname": "sales_invoice_no", "fieldtype": "Link", "options": "Sales Invoice"},
			{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date"},
			{"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date"},
			{"label": _("Invoice Amount"), "fieldname": "invoice_amount", "fieldtype": "Currency"},
			{"label": _("Paid Amount"), "fieldname": "paid_amount", "fieldtype": "Currency"},
			{"label": _("Outstanding Amount"), "fieldname": "outstanding_amount", "fieldtype": "Currency"},
			{"label": _("Territory"), "fieldname": "territory", "fieldtype": "Link", "options": "Territory"},
			{"label": _("Customer Group"), "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group"},
			{"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Data"},
			{"label": _("Currency"), "fieldname": "currency", "fieldtype": "Link", "options": "Currency"},
		]
		
	def get_data(self):
		self.data = []
		conditions = self.get_conditions()
		
		query = f"""
			SELECT 
				si.customer,
				si.name as sales_invoice_no,
				si.posting_date,
				si.due_date,
				si.grand_total as invoice_amount,
				si.outstanding_amount,
				(si.grand_total - si.outstanding_amount) as paid_amount,
				si.territory,
				si.customer_group,
				si.currency,
				GROUP_CONCAT(DISTINCT sp.sales_person SEPARATOR ', ') as sales_person
			FROM 
				`tabSales Invoice` si
			LEFT JOIN 
				`tabSales Team` sp ON si.name = sp.parent
			WHERE 
				si.docstatus = 1
				AND si.outstanding_amount > 0
				{conditions}
			GROUP BY 
				si.name
			ORDER BY 
				si.posting_date ASC
		"""
		
		self.data = frappe.db.sql(query, self.filters, as_dict=1)
		
	def get_conditions(self):
		conditions = []
		
		if self.filters.get("company"):
			conditions.append("si.company = %(company)s")
			
		if self.filters.get("customer"):
			conditions.append("si.customer = %(customer)s")
			
		if self.filters.get("customer_group"):
			conditions.append("si.customer_group = %(customer_group)s")
			
		if self.filters.get("territory"):
			conditions.append("si.territory = %(territory)s")
			
		if self.filters.get("sales_person"):
			conditions.append("sp.sales_person = %(sales_person)s")
			
		if self.filters.get("from_date"):
			conditions.append("si.posting_date >= %(from_date)s")
			
		if self.filters.get("to_date"):
			conditions.append("si.posting_date <= %(to_date)s")
			
		return " AND " + " AND ".join(conditions) if conditions else ""
