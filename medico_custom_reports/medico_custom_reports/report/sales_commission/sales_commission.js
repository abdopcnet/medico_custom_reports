// Copyright (c) 2024, abdopcnet@gmail.com and contributors
// For license information, please see license.txt

frappe.query_reports['sales_commission'] = {
	filters: [
		{
			fieldname: 'from_date',
			label: __('From Date'),
			fieldtype: 'Date',
			default: frappe.datetime.month_start(),
			mandatory: 1,
		},
		{
			fieldname: 'to_date',
			label: __('To Date'),
			fieldtype: 'Date',
			default: frappe.datetime.get_today(),
			mandatory: 1,
		},
		{
			fieldname: 'customer_name',
			label: __('Customer Name'),
			fieldtype: 'Link',
			options: 'Customer',
		},
	],
};
