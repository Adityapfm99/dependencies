from openerp.osv import fields,osv

class account_analytic_account(osv.osv):
	_inherit = "account.analytic.account"

	_columns = {
		"active": fields.boolean("Active"),
		"tag"	: fields.selection([('provinsi',"Provinsi"),('kota',"Kabupaten/Kota"),('gerai',"Gerai"),('perwakilan',"Perwakilan"),('other',"Lainnya")],"Category")
		# "perwakilan_ids": fields.many2many("account.analytic.perwakilan","analytic_account_perwakilan_rel")
	}

	_defaults ={
	"active" : True,
	"tag"	: "other",
	}