# Copyright (c) 2013, NODUX and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _

def execute(filters=None):
	#moificar columns y verificar filtros
	if not filters: filters = {}

	purchase_list = get_purchases(filters)
	columns = get_columns(purchase_list)

	if not purchase_list:
		msgprint(_("No record found"))
		return columns, purchase_list

	data = []
	for inv in purchase_list:
		row = [inv.name, inv.posting_date, inv.supplier, inv.supplier_name, inv.base_imponible,
		inv.total_taxes, inv.total, inv.residual_amount]
		data.append(row)

	return columns, data


def get_columns(purchase_list):
	"""return columns based on filters"""
	columns = [
		_("Invoice") + ":Link/Purchases Invoice One:120", _("Posting Date") + ":Date:80",
		_("Supplier Id") + "::120", _("Supplier Name") + "::120"]


	columns = columns + [_("Net Total") + ":Currency/currency:120"] + \
		[_("Total Tax") + ":Currency/currency:120", _("Grand Total") + ":Currency/currency:120",
		_("Outstanding Amount") + ":Currency/currency:120"]

	return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("company"): conditions += " and company=%(company)s"
	if filters.get("supplier"): conditions += " and supplier = %(supplier)s"

	if filters.get("from_date"): conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and posting_date <= %(to_date)s"

	return conditions

def get_purchases(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""select name, posting_date, supplier, supplier_name,
		base_imponible, total_taxes, total, residual_amount
		from `tabPurchases Invoice One`
		where docstatus = 1 %s order by posting_date desc, name desc""" %
		conditions, filters, as_dict=1)
