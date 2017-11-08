from openerp.osv import fields,osv

class gammu_phone(osv.osv):
	_name = "gammu.phone"

	def _compute_prefix(self,cr,uid,ids,field_names,args,context=None):
		if not context:context={}
		res = {}
		for phone in self.browse(cr,uid,ids):
			prefix=""
			if phone.phone_number.startswith("+"):
				prefix = "0"+phone.phone_number[3:6]
			else:
				prefix = phone.phone_number[0:4]
			res[phone.id]=prefix
		return res

	_columns = {
		"name"					: fields.char("Phone Name",required=True,),
		"phone_number"			: fields.char("Phone Number",required=True,help="use format +628123456789"),
		"config_file"			: fields.char("Config File Path",required=True),
		"phone_number_prefix"	: fields.function(_compute_prefix,type="char",
					string="Phone Prefix",store={'gammu.phone': (lambda self, cr, uid, ids, c={}: ids, ['phone_number'], 10)}),
		"provider"				: fields.char("Provider",required=True),
		"default"				: fields.boolean("Default Phone"),
		"active"				: fields.boolean("Useable"),
	}
	_order = "default desc,phone_number asc"
	_defaults = {
		"active":True,
	}
	def get_config_path(self,cr,uid,ids,phone_number,context=None):
		if not context:context={}
		config_file = False
		if not ids :
			if phone_number.startswith("+"):
				prefix = "0"+phone_number[3:6]
			else:
				prefix = phone_number[0:4]
			phone_id = self.search(cr,uid,[('phone_number_prefix','=',prefix)])
			if phone_id and phone_id[0]:
				phone = self.browse(cr,uid,phone_id)
				config_file = phone.config_file	
		else:
			phone = self.browse(cr,uid,ids)
			config_file = phone.config_file
		return config_file
