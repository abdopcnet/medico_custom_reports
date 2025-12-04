// Copyright (c) 2025, abdopcnet@gmail.com and contributors
// For license information, please see license.txt

frappe.query_reports['purchase_invoice_tax_report'] = {
	filters: [
		{
			fieldname: 'from_date',
			label: __('من تاريخ'),
			fieldtype: 'Date',
			default: frappe.datetime.month_start(),
			reqd: 1,
		},
		{
			fieldname: 'to_date',
			label: __('إلى تاريخ'),
			fieldtype: 'Date',
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: 'company',
			label: __('الشركة'),
			fieldtype: 'Link',
			options: 'Company',
		},
		{
			fieldname: 'supplier_name',
			label: __('اسم المورد'),
			fieldtype: 'Link',
			options: 'Supplier',
		},
	],
};
