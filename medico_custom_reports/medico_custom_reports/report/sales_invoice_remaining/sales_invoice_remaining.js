// Copyright (c) 2025, abdopcnet@gmail.com and contributors
// For license information, please see license.txt

frappe.query_reports['sales invoice remaining'] = {
	filters: [
		{
			fieldname: 'company',
			label: __('Company'),
			fieldtype: 'Link',
			options: 'Company',
			default: frappe.defaults.get_user_default('Company'),
			reqd: 1,
		},
		{
			fieldname: 'from_date',
			label: __('From Date'),
			fieldtype: 'Date',
			default: frappe.datetime.year_start(),
		},
		{
			fieldname: 'to_date',
			label: __('To Date'),
			fieldtype: 'Date',
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: 'customer',
			label: __('Customer'),
			fieldtype: 'Link',
			options: 'Customer',
		},
		{
			fieldname: 'customer_group',
			label: __('Customer Group'),
			fieldtype: 'Link',
			options: 'Customer Group',
		},
		{
			fieldname: 'territory',
			label: __('Territory'),
			fieldtype: 'Link',
			options: 'Territory',
		},
		{
			fieldname: 'sales_person',
			label: __('Sales Person'),
			fieldtype: 'Link',
			options: 'Sales Person',
		},
		{
			fieldname: 'sales_partner',
			label: __('Sales Partner'),
			fieldtype: 'Link',
			options: 'Sales Partner',
		},
	],

	onload: function (report) {
		// Add custom buttons if needed
		report.page.add_inner_button(__('Payment Entry'), function () {
			frappe.set_route('List', 'Payment Entry');
		});

		report.page.add_inner_button(__('Payment Request'), function () {
			frappe.set_route('List', 'Payment Request');
		});
	},

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		// Highlight overdue invoices
		if (column.fieldname == 'outstanding_amount' && data && data.due_date) {
			var due_date = frappe.datetime.str_to_obj(data.due_date);
			var today = new Date();

			if (due_date < today) {
				value = `<span style="color: red; font-weight: bold;">${value}</span>`;
			}
		}

		return value;
	},
};
