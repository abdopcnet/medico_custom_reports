# Copyright (c) 2025, abdopcnet@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}

    columns = [
        {
            "fieldname": "name",
            "label": _("فاتورة الشراء"),
            "fieldtype": "Link",
            "options": "Purchase Invoice",
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
            "fieldname": "supplier_name",
            "label": _("اسم المورد"),
            "fieldtype": "Link",
            "options": "Supplier",
        },
        {
            "fieldname": "tax_id",
            "label": _("رقم الضريبة"),
            "fieldtype": "Data",
        },
        {
            "fieldname": "taxes_and_charges",
            "label": _("الضرائب والرسوم"),
            "fieldtype": "Data",
        },
        {
            "fieldname": "total_taxes_and_charges",
            "label": _("إجمالي الضرائب والرسوم"),
            "fieldtype": "Currency",
        },
    ]

    # Base SQL (row per invoice)
    query = """
        SELECT
            `tabPurchase Invoice`.`name`,
            `tabPurchase Invoice`.`posting_date`,
            `tabPurchase Invoice`.`due_date`,
            `tabPurchase Invoice`.`company`,
            `tabSupplier`.`name` AS supplier_name,
            `tabPurchase Invoice`.`tax_id`,
            `tabPurchase Invoice`.`taxes_and_charges`,
            `tabPurchase Invoice`.`total_taxes_and_charges` AS total_taxes_and_charges
        FROM `tabPurchase Invoice`
        LEFT JOIN `tabSupplier` ON `tabPurchase Invoice`.`supplier` = `tabSupplier`.`name`
    """

    where_conditions = []
    params = {}

    if filters.get("from_date") and filters.get("to_date"):
        where_conditions.append("(`tabPurchase Invoice`.`posting_date` BETWEEN %(from_date)s AND %(to_date)s)")
        params["from_date"] = filters["from_date"]
        params["to_date"] = filters["to_date"]

    if filters.get("supplier_name"):
        # Link filter returns Supplier.name
        where_conditions.append("`tabPurchase Invoice`.`supplier` = %(supplier_name)s")
        params["supplier_name"] = filters["supplier_name"]

    if filters.get("company"):
        where_conditions.append("`tabPurchase Invoice`.`company` = %(company)s")
        params["company"] = filters["company"]

    if where_conditions:
        query = f"{query} WHERE " + " AND ".join(where_conditions)

    data = frappe.db.sql(query, params, as_dict=True)

    return columns, data