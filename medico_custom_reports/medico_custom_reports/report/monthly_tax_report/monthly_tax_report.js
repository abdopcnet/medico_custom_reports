// Copyright (c) 2024, Future Dev and contributors
// For license information, please see license.txt
/* eslint-disable */

// Define the query report for the Monthly Tax Report
frappe.query_reports['Monthly Tax Report'] = {
	// Function executed when the report is loaded
	onload() {
		// Add a breadcrumb for navigation
		frappe.breadcrumbs.add('Accounts');
	},
	// Define the filters for the report
	filters: [
		{
			// Filter for the starting date of the report
			fieldname: 'from_date',
			label: __('From Date'),
			fieldtype: 'Date',
			reqd: 1, // Indicates that this field is required
			default: frappe.datetime.month_start(), // Default value is the start of the current month
		},
		{
			// Filter for the ending date of the report
			fieldname: 'to_date',
			label: __('To Date'),
			fieldtype: 'Date',
			reqd: 1, // Indicates that this field is required
			default: frappe.datetime.now_date(), // Default value is the current date
		},
		{
			// Optional filter for Company
			fieldname: 'company',
			label: __('Company'),
			fieldtype: 'Link',
			options: 'Company',
		},
	],
	// Formatter function to style the report table cells
	formatter: function (value, row, column, data, default_formatter) {
		// Define styles for different voucher types
		const styles = {
			Sales: 'color: blue; font-weight: bold;', // Style for Sales
			Purchase: 'color: green; font-weight: bold;', // Style for Purchase
			'Total Difference': 'color: red; font-weight: bold;', // Style for Total Difference
		};

		// Apply the corresponding style based on voucher type
		let style = styles[data.voucher_type] || ''; // Default to an empty style if not found
		value = $(`<span style="${style} padding: 5px;">${value || ''}</span>`); // Wrap value in a span with style and padding
		return value.wrap('<p></p>').parent().html(); // Wrap the styled span in a paragraph and return HTML
	},
};
