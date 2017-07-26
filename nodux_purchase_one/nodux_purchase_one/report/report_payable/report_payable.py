# Copyright (c) 2013, NODUX and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _

def execute(filters=None):
	if not filters: filters = {}

	purchase_list = get_purchases(filters)
	columns = get_columns(purchase_list)

	if not purchase_list:
		msgprint(_("No record found"))
		return columns, purchase_list

	data = []
	for inv in purchase_list:
		row = [inv.name, inv.posting_date, inv.customer, inv.total,
		inv.paid_amount, inv.residual_amount]
		data.append(row)
	return columns, data


def get_columns(purchase_list):
	"""return columns based on filters"""
	columns = [
		_("Invoice") + ":Link/Purchases Invoice One:150", _("Posting Date") + ":Date:80",
		_("Supplier Name") + "::360"]

	columns = columns + [_("Grand Total") + ":Currency/currency:120",
		_("Payment Amount") + ":Currency/currency:120",
		_("Pending Amount") + ":Currency/currency:120"]

	return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("company"): conditions += " and company=%(company)s"
	if filters.get("customer"): conditions += " and customer = %(customer)s"
	if filters.get("from_date"): conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and posting_date <= %(to_date)s"

	return conditions

def get_purchases(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""select name, posting_date, customer, customer_name,
		total, paid_amount, residual_amount
		from `tabPurchases Invoice One`
		where docstatus = 1 and status ='Confirmed' %s order by posting_date desc, name desc""" %
		conditions, filters, as_dict=1)
