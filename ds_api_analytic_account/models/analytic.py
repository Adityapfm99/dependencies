from openerp.osv import fields,osv

class account_analytic_account(osv.osv):
	_inherit = "account.analytic.account"

	_columns = {
		"active": fields.boolean("Active"),
		"tag"	: fields.selection([('provinsi',"Provinsi"),('kota',"Kabupaten/Kota"),('gerai',"Gerai"),('other',"Lainnya")],"Category")
	}

	_defaults ={
	"active" : True,
	"tag"	: "other",
	}