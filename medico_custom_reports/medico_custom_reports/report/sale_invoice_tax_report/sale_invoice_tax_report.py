# Copyright (c) 2025, abdopcnet@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}

    columns = [
        {
            "fieldname": "name",
            "label": _("فاتورة المبيعات"),
            "fieldtype": "Link",
            "options": "Sales Invoice",
        },
        {
            "fieldname": "posting_date",
            "label": _("تاريخ النشر"),
            "fieldtype": "Date",
        },
        {
            "fieldname": "due_date",
            "label": _("تاريخ الاستحقاق"),
            "fieldtype": "Date",
        },
        {
            "fieldname": "company",
            "label": _("الشركة"),
            "fieldtype": "Link",
            "options": "Company",
        },
        {
            "fieldname": "customer_name",
            "label": _("اسم العميل"),
            "fieldtype": "Link",
            "options": "Customer",
        },
        {
            "fieldname": "tax_id",
            "label": _("رقم الضريبة"),
            "fieldtype": "Data",
        },
        {
            "fieldname": "custom_sales_invoice_number",
            "label": _("رقم الفاتورة المخصص"),
            "fieldtype": "Data",
        },
        {
            "fieldname": "taxes_and_charges",
            "label": _("الضرائب والرسوم"),
            "fieldtype": "Data",
        },
        {
            "fieldname": "custom_tax_template",
            "label": _("قالب الضريبة المخصص"),
            "fieldtype": "Data",
        },
        {
            "fieldname": "total_taxes_and_charges",
            "label": _("إجمالي الضرائب والرسوم"),
            "fieldtype": "Currency",
        },
    ]

    # Base SQL query (row per invoice)
    query = """
        SELECT
            si.name,
            si.posting_date,
            si.due_date,
            si.company,
            c.customer_name,
            si.tax_id,
            si.custom_sales_invoice_number,
            si.taxes_and_charges,
            cg.custom_tax_template,
            si.total_taxes_and_charges AS total_taxes_and_charges
        FROM `tabSales Invoice` si
        LEFT JOIN `tabCustomer` c ON si.customer = c.name
        LEFT JOIN `tabCustomer Group` cg ON si.customer_group = cg.name
    """

    # WHERE conditions
    where_conditions = []
    params = {}

    if filters.get("from_date") and filters.get("to_date"):
        where_conditions.append("(si.posting_date BETWEEN %(from_date)s AND %(to_date)s)")
        params["from_date"] = filters["from_date"]
        params["to_date"] = filters["to_date"]

    if filters.get("customer_name"):
        # Filter by Customer (Link field provides Customer.name)
        where_conditions.append("si.customer = %(customer_name)s")
        params["customer_name"] = filters["customer_name"]

    if filters.get("company"):
        where_conditions.append("si.company = %(company)s")
        params["company"] = filters["company"]

    if where_conditions:
        query = f"{query} WHERE " + " AND ".join(where_conditions)

    data = frappe.db.sql(query, params, as_dict=True)

    return columns, data