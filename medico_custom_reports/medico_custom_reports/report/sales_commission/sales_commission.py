# Copyright (c) 2025, abdopcnet@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, flt


def execute(filters=None):
	"""
	Execute function for Sales Commission Report (تقرير عمولة مناديب البيع)
	
	Args:
		filters (dict): Dictionary containing filter values
		
	Returns:
		tuple: (columns, data) - columns definition and data rows
	"""
	if not filters:
		filters = frappe._dict({})
	
	# Get columns definition
	columns = get_columns()
	
	# Get data based on filters
	data = get_data(filters)
	
	return columns, data


def get_columns():
	"""Define report columns"""
	columns = [
		{
			"fieldname": "sales_invoice",
			"label": _("رقم الفاتورة"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
		},
		{
			"fieldname": "company",
			"label": _("الشركة"),
			"fieldtype": "Link",
			"options": "Company",
		},
		{
			"fieldname": "customer",
			"label": _("العميل"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname": "posting_date",
			"label": _("تاريخ الإثبات"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "customer_invoice_reference_no",
			"label": _("رقم الفاتورة المخصص"),
			"fieldtype": "Data",
		},
		{
			"fieldname": "grand_total",
			"label": _("الإجمالي"),
			"fieldtype": "Currency",
		},
		{
			"fieldname": "subtotal_without_vat",
			"label": _("المجموع الفرعي بدون ضريبة"),
			"fieldtype": "Currency",
		},
		{
			"fieldname": "sales_person",
			"label": _("مندوب المبيعات"),
			"fieldtype": "Link",
			"options": "Sales Person",
		},
		{
			"fieldname": "commission_rate",
			"label": _("نسبة العمولة (%)"),
			"fieldtype": "Percent",
		},
		{
			"fieldname": "total_paid",
			"label": _("إجمالي المدفوع"),
			"fieldtype": "Currency",
		},
		{
			"fieldname": "total_papers",
			"label": _("إجمالي الأوراق"),
			"fieldtype": "Int",
		},
		{
			"fieldname": "stamp_value",
			"label": _("قيمة الدمغة"),
			"fieldtype": "Currency",
		},
		{
			"fieldname": "net_amount_paid",
			"label": _("صافي المبلغ المدفوع"),
			"fieldtype": "Currency",
		},
		{
			"fieldname": "amount_eligible_for_commission",
			"label": _("المبلغ الخاضع للعمولة"),
			"fieldtype": "Currency",
		},
		{
			"fieldname": "incentives",
			"label": _("قيمة العمولة"),
			"fieldtype": "Currency",
		}
	]
	
	return columns


def get_data(filters):
	"""
	Get report data based on filters
	
	Args:
		filters (dict): Filter dictionary containing from_date, to_date, etc.
		
	Returns:
		list: List of dictionaries containing report data
	"""
	# Build SQL query with CTEs
	query = """
		WITH invoice_payments AS (
			SELECT
				per.reference_name AS invoice_name,
				SUM(per.allocated_amount) AS total_paid
			FROM `tabPayment Entry` pe
			INNER JOIN `tabPayment Entry Reference` per ON per.parent = pe.name
			WHERE pe.docstatus = 1
				AND per.reference_doctype = 'Sales Invoice'
			GROUP BY per.reference_name
		),
		
		invoice_papers AS (
			SELECT
				per.reference_name AS invoice_name,
				SUM(COALESCE(pe.custom_عدد_اوراق_العقد, 0)) AS total_contract_papers
			FROM `tabPayment Entry` pe
			INNER JOIN `tabPayment Entry Reference` per ON per.parent = pe.name
			WHERE pe.docstatus = 1
				AND per.reference_doctype = 'Sales Invoice'
			GROUP BY per.reference_name
		),
		
		invoice_vat AS (
			SELECT
				parent AS invoice_name,
				SUM(COALESCE(base_tax_amount_after_discount_amount, 0)) AS invoice_vat_total
			FROM `tabSales Taxes and Charges`
			WHERE docstatus = 1
			GROUP BY parent
		),
		
		sales_persons AS (
			SELECT
				parent AS invoice_name,
				sales_person
			FROM `tabSales Team`
			WHERE parenttype = 'Sales Invoice'
		)
		
		SELECT
			si.name AS sales_invoice,
			si.company,
			si.customer,
			si.posting_date,
			si.custom_sales_invoice_number AS customer_invoice_reference_no,
			si.grand_total,
			(si.grand_total - COALESCE(si.total_taxes_and_charges, 0)) AS subtotal_without_vat,
			COALESCE(ip.total_paid, 0) AS total_paid,
			COALESCE(ipapers.total_contract_papers, 0) AS total_papers,
			(COALESCE(ipapers.total_contract_papers, 0) * 3 * 0.90) AS stamp_value,
			sp.sales_person,
			COALESCE(st.commission_rate, 0) AS commission_rate,
			COALESCE(iv.invoice_vat_total, 0) AS invoice_vat_total,
			/* Net payable المعدل */
			(
				COALESCE(ip.total_paid, 0) -
				(
					COALESCE(ip.total_paid, 0) * 0.01 +
					(
						(
							CASE WHEN si.grand_total BETWEEN 51 AND 250 THEN (si.grand_total - 50) * 0.048 ELSE 0 END +
							CASE WHEN si.grand_total BETWEEN 251 AND 500 THEN (si.grand_total - 50) * 0.052 ELSE 0 END +
							CASE WHEN si.grand_total BETWEEN 501 AND 1000 THEN (si.grand_total - 50) * 0.056 ELSE 0 END +
							CASE WHEN si.grand_total BETWEEN 1001 AND 5000 THEN (si.grand_total - 50) * 0.06 ELSE 0 END +
							CASE WHEN si.grand_total BETWEEN 5001 AND 10000 THEN (si.grand_total - 50) * 0.064 ELSE 0 END +
							CASE WHEN si.grand_total > 10000 THEN (si.grand_total - 50) * 0.024 ELSE 0 END
						) * (CASE WHEN si.grand_total > 0 THEN COALESCE(ip.total_paid, 0) / si.grand_total ELSE 0 END)
					) +
					(COALESCE(ipapers.total_contract_papers, 0) * 3 * 0.90) +
					((COALESCE(iv.invoice_vat_total, 0) * 0.20) *
						(CASE WHEN si.grand_total > 0 THEN COALESCE(ip.total_paid, 0) / si.grand_total ELSE 0 END))
				)
			) AS net_amount_paid,
			/* المبلغ الخاضع للعمولة */
			(
				(
					COALESCE(ip.total_paid, 0) -
					(
						COALESCE(ip.total_paid, 0) * 0.01 +
						(
							(
								CASE WHEN si.grand_total BETWEEN 51 AND 250 THEN (si.grand_total - 50) * 0.048 ELSE 0 END +
								CASE WHEN si.grand_total BETWEEN 251 AND 500 THEN (si.grand_total - 50) * 0.052 ELSE 0 END +
								CASE WHEN si.grand_total BETWEEN 501 AND 1000 THEN (si.grand_total - 50) * 0.056 ELSE 0 END +
								CASE WHEN si.grand_total BETWEEN 1001 AND 5000 THEN (si.grand_total - 50) * 0.06 ELSE 0 END +
								CASE WHEN si.grand_total BETWEEN 5001 AND 10000 THEN (si.grand_total - 50) * 0.064 ELSE 0 END +
								CASE WHEN si.grand_total > 10000 THEN (si.grand_total - 50) * 0.024 ELSE 0 END
							) * (CASE WHEN si.grand_total > 0 THEN COALESCE(ip.total_paid, 0) / si.grand_total ELSE 0 END)
						) +
						(COALESCE(ipapers.total_contract_papers, 0) * 3 * 0.90) +
						((COALESCE(iv.invoice_vat_total, 0) * 0.20) *
							(CASE WHEN si.grand_total > 0 THEN COALESCE(ip.total_paid, 0) / si.grand_total ELSE 0 END))
					)
				)
				- COALESCE(iv.invoice_vat_total, 0)
			) AS amount_eligible_for_commission,
			/* قيمة العمولة */
			(
				(
					COALESCE(ip.total_paid, 0) -
					(
						COALESCE(ip.total_paid, 0) * 0.01 +
						(
							(
								CASE WHEN si.grand_total BETWEEN 51 AND 250 THEN (si.grand_total - 50) * 0.048 ELSE 0 END +
								CASE WHEN si.grand_total BETWEEN 251 AND 500 THEN (si.grand_total - 50) * 0.052 ELSE 0 END +
								CASE WHEN si.grand_total BETWEEN 501 AND 1000 THEN (si.grand_total - 50) * 0.056 ELSE 0 END +
								CASE WHEN si.grand_total BETWEEN 1001 AND 5000 THEN (si.grand_total - 50) * 0.06 ELSE 0 END +
								CASE WHEN si.grand_total BETWEEN 5001 AND 10000 THEN (si.grand_total - 50) * 0.064 ELSE 0 END +
								CASE WHEN si.grand_total > 10000 THEN (si.grand_total - 50) * 0.024 ELSE 0 END
							) * (CASE WHEN si.grand_total > 0 THEN COALESCE(ip.total_paid, 0) / si.grand_total ELSE 0 END)
						) +
						(COALESCE(ipapers.total_contract_papers, 0) * 3 * 0.90) +
						(
							(COALESCE(iv.invoice_vat_total, 0) * 0.20) *
							(CASE WHEN si.grand_total > 0 THEN COALESCE(ip.total_paid, 0) / si.grand_total ELSE 0 END)
						)
					)
					- COALESCE(iv.invoice_vat_total, 0)
				)
				* (COALESCE(st.commission_rate, 0) / 100)
			) AS incentives
		FROM `tabSales Invoice` si
		LEFT JOIN invoice_payments ip ON ip.invoice_name = si.name
		LEFT JOIN invoice_papers ipapers ON ipapers.invoice_name = si.name
		LEFT JOIN invoice_vat iv ON iv.invoice_name = si.name
		LEFT JOIN sales_persons sp ON sp.invoice_name = si.name
		LEFT JOIN `tabSales Team` st
			ON st.parent = si.name
			AND st.parenttype = 'Sales Invoice'
			AND st.sales_person = sp.sales_person
		WHERE si.docstatus = 1
	"""
	
	# Get conditions and parameters
	conditions, params = get_conditions(filters)
	
	if conditions:
		query += " AND " + conditions
	
	query += " ORDER BY si.posting_date DESC, si.name DESC"
	
	# Execute query using frappe.db.sql with parameters
	if params:
		data = frappe.db.sql(query, params, as_dict=True)
	else:
		data = frappe.db.sql(query, as_dict=True)
	
	# Ensure all numeric fields are properly formatted
	for row in data:
		row["grand_total"] = flt(row.get("grand_total", 0))
		row["total_paid"] = flt(row.get("total_paid", 0))
		row["net_amount_paid"] = flt(row.get("net_amount_paid", 0))
		row["amount_eligible_for_commission"] = flt(row.get("amount_eligible_for_commission", 0))
		row["incentives"] = flt(row.get("incentives", 0))
		row["commission_rate"] = flt(row.get("commission_rate", 0))
		row["total_papers"] = int(row.get("total_papers", 0))
		row["stamp_value"] = flt(row.get("stamp_value", 0))
		row["subtotal_without_vat"] = flt(row.get("subtotal_without_vat", 0))
	
	return data


def get_conditions(filters):
	"""
	Build WHERE conditions based on filters with proper parameterization
	
	Args:
		filters (dict): Filter dictionary
		
	Returns:
		tuple: (conditions_string, params_dict) - SQL WHERE conditions and parameters
	"""
	conditions = []
	params = {}
	
	if filters.get("from_date"):
		from_date = getdate(filters.get("from_date"))
		conditions.append("si.posting_date >= %(from_date)s")
		params["from_date"] = from_date
	
	if filters.get("to_date"):
		to_date = getdate(filters.get("to_date"))
		conditions.append("si.posting_date <= %(to_date)s")
		params["to_date"] = to_date
	
	if filters.get("company"):
		conditions.append("si.company = %(company)s")
		params["company"] = filters.get("company")
	
	if filters.get("customer"):
		conditions.append("si.customer = %(customer)s")
		params["customer"] = filters.get("customer")
	
	if filters.get("sales_person"):
		conditions.append("sp.sales_person = %(sales_person)s")
		params["sales_person"] = filters.get("sales_person")
	
	if conditions:
		return " AND ".join(conditions), params
	
	return "", {}
