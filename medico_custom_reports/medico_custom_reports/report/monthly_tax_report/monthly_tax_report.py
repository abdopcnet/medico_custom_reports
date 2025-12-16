import frappe
from frappe import _
from frappe.utils import formatdate

# Main function to execute the report with provided filters
def execute(filters=None):
    return MonthlyTaxReport(filters).run()

class MonthlyTaxReport:
    def __init__(self, filters=None):
        # Initialize the class with filters and data structures
        self.filters = frappe._dict(filters or {})
        self.columns = []
        self.data = []
        self.total_sales_invoices = 0
        self.total_purchase_invoices = 0

    # Run the report by fetching columns and tax data
    def run(self):
        self.get_columns()   
        self.get_tax_data()  
        return self.columns, self.data  

    # Fetch tax data from sales and purchase invoices
    def get_tax_data(self):
        # helper to round values to 4 decimals consistently
        def r4(v):
            try:
                return round(float(v), 4) if v is not None else 0.0
            except Exception:
                return 0.0

        # Query for sales tax data
        sales_where_company = " AND `tabSales Invoice`.company = %(company)s" if self.filters.get("company") else ""
        sales_sql = f"""
            SELECT 
                `tabSales Taxes and Charges`.rate AS tax_rate,
                SUM(`tabSales Taxes and Charges`.tax_amount) AS total_tax_amount,
                SUM(`tabSales Invoice`.grand_total) AS total_net_amount,
                COUNT(DISTINCT `tabSales Invoice`.name) AS inv_qty
            FROM 
                `tabSales Taxes and Charges`
            JOIN 
                `tabSales Invoice` ON `tabSales Taxes and Charges`.parent = `tabSales Invoice`.name
            WHERE 
                `tabSales Taxes and Charges`.docstatus = 1
                AND `tabSales Invoice`.posting_date BETWEEN %(from_date)s AND %(to_date)s{sales_where_company}
            GROUP BY 
                `tabSales Taxes and Charges`.rate
            ORDER BY 
                `tax_rate`
        """
        sales_tax_data = frappe.db.sql(sales_sql, self.filters, as_dict=True)

        # Query for purchase tax data
        purchase_where_company = " AND `tabPurchase Invoice`.company = %(company)s" if self.filters.get("company") else ""
        purchase_sql = f"""
            SELECT 
                `tabPurchase Taxes and Charges`.rate AS tax_rate,
                SUM(`tabPurchase Taxes and Charges`.tax_amount) AS total_tax_amount,
                SUM(`tabPurchase Invoice`.grand_total) AS total_net_amount,
                COUNT(DISTINCT `tabPurchase Invoice`.name) AS inv_qty
            FROM 
                `tabPurchase Taxes and Charges`
            JOIN 
                `tabPurchase Invoice` ON `tabPurchase Taxes and Charges`.parent = `tabPurchase Invoice`.name
            WHERE 
                `tabPurchase Taxes and Charges`.docstatus = 1
                AND `tabPurchase Invoice`.posting_date BETWEEN %(from_date)s AND %(to_date)s{purchase_where_company}
            GROUP BY 
                `tabPurchase Taxes and Charges`.rate
            ORDER BY 
                `tax_rate`
        """
        purchase_tax_data = frappe.db.sql(purchase_sql, self.filters, as_dict=True)

        # Process sales tax data
        for row in sales_tax_data:
            self.data.append({
                "voucher_type": "Sales",
                "tax_rate": r4(row.tax_rate),
                "total_tax_amount": r4(row.total_tax_amount),
                "total_net_amount": r4(row.total_net_amount),
                "inv_qty": row.inv_qty,
            })

        # Add a total line after sales data
        self.data.append({
            "voucher_type": "Total Sales",
            "tax_rate": None,
            "total_tax_amount": r4(sum(row['total_tax_amount'] for row in sales_tax_data if row['total_tax_amount'] is not None)),
            "total_net_amount": r4(sum(row['total_net_amount'] for row in sales_tax_data if row['total_net_amount'] is not None)),
            "inv_qty": sum(row.inv_qty for row in sales_tax_data),
        })

        # Add a blank line after total sales
        self.data.append({
            "voucher_type": "------",
            "tax_rate": "------",
            "total_tax_amount": "------",
            "total_net_amount": "------",
            "inv_qty": "------",
        })

        # Process purchase tax data
        for row in purchase_tax_data:
            self.data.append({
                "voucher_type": "Purchase",
                "tax_rate": r4(row.tax_rate),
                "total_tax_amount": r4(row.total_tax_amount),
                "total_net_amount": r4(row.total_net_amount),
                "inv_qty": row.inv_qty,
            })

        # Add a total line after purchase data
        self.data.append({
            "voucher_type": "Total Purchases",
            "tax_rate": None,
            "total_tax_amount": r4(sum(row['total_tax_amount'] for row in purchase_tax_data if row['total_tax_amount'] is not None)),
            "total_net_amount": r4(sum(row['total_net_amount'] for row in purchase_tax_data if row['total_net_amount'] is not None)),
            "inv_qty": sum(row.inv_qty for row in purchase_tax_data),
        })

        # Add a blank line after total purchases
        self.data.append({
            "voucher_type": "------",
            "tax_rate": "------",
            "total_tax_amount": "------",
            "total_net_amount": "------",
            "inv_qty": "------",
        })

        # Calculate totals for sales and purchases
        total_sales_net_amount = sum(row['total_net_amount'] for row in sales_tax_data if row['total_net_amount'] is not None)
        total_sales_tax_amount = sum(row['total_tax_amount'] for row in sales_tax_data if row['total_tax_amount'] is not None)
        total_purchase_net_amount = sum(row['total_net_amount'] for row in purchase_tax_data if row['total_net_amount'] is not None)
        total_purchase_tax_amount = sum(row['total_tax_amount'] for row in purchase_tax_data if row['total_tax_amount'] is not None)

        # Calculate the total invoice quantity by summing sales and purchase invoice quantities
        total_sales_inv_qty = sum(row.inv_qty for row in sales_tax_data)
        total_purchase_inv_qty = sum(row.inv_qty for row in purchase_tax_data)

        # Calculate the tax rates and their difference, avoiding division by zero
        sales_rate = (total_sales_tax_amount / total_sales_net_amount * 100) if total_sales_net_amount else 0
        purchase_rate = (total_purchase_tax_amount / total_purchase_net_amount * 100) if total_purchase_net_amount else 0
        tax_rate_difference = r4(sales_rate - purchase_rate)

        # Add a total difference row at the end of the report with red formatting
        self.data.append({
            "voucher_type": "Total Difference",
            "tax_rate": tax_rate_difference,
            "total_tax_amount": r4(total_sales_tax_amount - total_purchase_tax_amount),
            "total_net_amount": r4(total_sales_net_amount - total_purchase_net_amount),
            "inv_qty": total_sales_inv_qty + total_purchase_inv_qty,
            "color": "red",
        })

    # Define the columns for the report
    def get_columns(self):
        self.columns = [
            {"fieldname": "voucher_type", "label": _("Voucher Type"), "fieldtype": "Data", "width": 200},
            {"fieldname": "tax_rate", "label": _("Tax Rate (%)"), "fieldtype": "Float", "precision": 4, "width": 200},
            {"fieldname": "total_tax_amount", "label": _("Total Tax Amount"), "fieldtype": "Currency", "precision": 4, "width": 200},
            {"fieldname": "total_net_amount", "label": _("Total Net Amount"), "fieldtype": "Currency", "precision": 4, "width": 200},
            {"fieldname": "inv_qty", "label": _("Invoice Quantity"), "fieldtype": "Int", "width": 200},
        ]
