from openerp.osv import fields,osv

class account_analytic_account(osv.osv):
	_inherit = "account.analytic.account"

	_columns = {
		"active": fields.boolean("Active"),
		"alias_name": fields.char("Alias Name"),
		"rds_id"	: fields.integer("ID RDS"),
		"tag"	: fields.selection([('head_office',"Head Office"),
			('region','Region'),
			('provinsi',"Provinsi"),
			('kota',"Kabupaten/Kota"),
			('gerai',"Gerai"),
			('toko','Toko'),
			('cabang','Cabang'),
			('transit','Transit'),
			('agen','Agen'),
			('pusat_transitan','Pusat Transitan'),
			('perwakilan',"Perwakilan"),
			('other',"Lainnya")],"Category"),
		# "perwakilan_ids": fields.many2many("account.analytic.perwakilan","analytic_account_perwakilan_rel")
		"alamat_lengkap": fields.text("Alamat Lengkap")
	}

	_defaults ={
	"active" : True,
	"tag"	: "other",
	}