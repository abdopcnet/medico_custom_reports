// Copyright (c) 2024, abdopcnet@gmail.com and contributors
// For license information, please see license.txt

frappe.query_reports['sales_commission'] = {
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
			default: frappe.datetime.month_end(),
			reqd: 1,
		},
		{
			fieldname: 'company',
			label: __('الشركة'),
			fieldtype: 'Link',
			options: 'Company',
		},
		{
			fieldname: 'customer',
			label: __('العميل'),
			fieldtype: 'Link',
			options: 'Customer',
		},
		{
			fieldname: 'sales_person',
			label: __('مندوب المبيعات'),
			fieldtype: 'Link',
			options: 'Sales Person',
		},
	],
};
