
from openerp.osv import osv,fields
from openerp.http import request

class needaction_mixion_custom(osv.osv):
	_name = "needaction.mixin.custom"

	_rec_name = "model_id"
	_columns = {
		"model_id"			: fields.many2one("ir.model","Model"),
		"usage"				: fields.selection([('model','Model'),('menu',"Menu")],"Usage"),
		"menu_id"			: fields.many2one("ir.ui.menu","Menu"),
		"act_window_id" 	: fields.many2one("ir.actions.act_window","Action Window"),
		"act_client_id"		: fields.many2one("ir.actions.client","Action Client"),
		"default_domain"	: fields.char("Forced Domain"),
		"default_count"		: fields.integer("Forced Count"),
	}

	_defaults = {
		"usage":"model",
		"default_count":0,
		"default_domain":"False",
	}

class ir_ui_menu(osv.osv):
	_inherit = 'ir.ui.menu'

	def get_needaction_data(self, cr, uid, ids, context=None):
		""" Return for each menu entry of ids :
			- if it uses the needaction mechanism (needaction_enabled)
			- the needaction counter of the related action, taking into account
			  the action domain
		"""
		mixin_custom_pool=self.pool.get('needaction.mixin.custom')
		mixin_custom_ids = mixin_custom_pool.search(cr,uid,[])
		mixin_custom = mixin_custom_pool.browse(cr, uid, mixin_custom_ids)
		mixer_menu = {}
		mixer_model = {}
		for m in mixin_custom:
			if m.usage=='model':
				mixer_model.update({
					m.menu_id.id:{
									'default_domain':m.default_domain,
									'default_count':m.default_count,
										}
									})
			else:
				mixer_menu.update({
					m.menu_id.id:{
						'act_window_id':m.act_window_id,
						'act_client_id':m.act_client_id,
						'default_domain':m.default_domain,
						'default_count':m.default_count,
						} 
					})

		if context is None:
			context = {}
		res = {}
		menu_ids = set()
		for menu in self.browse(cr, uid, ids, context=context):
			menu_ids.add(menu.id)
			ctx = None
			if menu.action and menu.action.type in ('ir.actions.act_window', 'ir.actions.client') and menu.action.context:
				try:
					# use magical UnquoteEvalContext to ignore undefined client-side variables such as `active_id`
					eval_ctx = tools.UnquoteEvalContext(**context)
					ctx = eval(menu.action.context, locals_dict=eval_ctx, nocopy=True) or None
				except Exception:
					# if the eval still fails for some reason, we'll simply skip this menu
					pass
			menu_ref = ctx and ctx.get('needaction_menu_ref')
			if menu_ref:
				if not isinstance(menu_ref, list):
					menu_ref = [menu_ref]
				model_data_obj = self.pool.get('ir.model.data')
				for menu_data in menu_ref:
					try:
						model, id = model_data_obj.get_object_reference(cr, uid, menu_data.split('.')[0], menu_data.split('.')[1])
						if (model == 'ir.ui.menu'):
							menu_ids.add(id)
					except Exception:
						pass

		menu_ids = list(menu_ids)

		for menu in self.browse(cr, uid, menu_ids, context=context):
			res[menu.id] = {
				'needaction_enabled': False,
				'needaction_counter': False,
			}
			if menu.id in mixer_model:
				enabled = mixer_model.get(menu.id).get('default_count',0)>=1 and True or False 
				res[menu.id]['needaction_enabled'] = enabled
				
				if mixer_model.get(menu.id).get('default_count',0)>=1 and True or False:
					if menu.action and menu.action.type in ('ir.actions.act_window', 'ir.actions.client') and menu.action.res_model:
						if menu.action.res_model in self.pool:
							obj = self.pool[menu.action.res_model]
							if obj._needaction:
								if menu.action.type == 'ir.actions.act_window':
									dom = menu.action.domain and eval(menu.action.domain, {'uid': uid}) or []
								else:
									dom = eval(menu.action.params_store or '{}', {'uid': uid}).get('domain')
								# res[menu.id]['needaction_enabled'] = obj._needaction
								res[menu.id]['needaction_counter'] = obj._needaction_count(cr, uid, dom, context=context)
				else:
					res[menu.id]['needaction_counter'] = mixer_model.get(menu.id).get('default_count',0)
			elif menu.id in mixer_menu:
				enabled = mixer_menu.get(menu.id).get('default_count',0)>=1 and True or False 
				res[menu.id]['needaction_enabled'] = enabled
				if mixer_menu.get(menu.id).get('default_count',0)>=1 and True or False:
					if menu.action and menu.action.type in ('ir.actions.act_window', 'ir.actions.client') and menu.action.res_model:
						if menu.action.res_model in self.pool:
							obj = self.pool[menu.action.res_model]
							if obj._needaction:
								if menu.action.type == 'ir.actions.act_window':
									dom = menu.action.domain and eval(menu.action.domain, {'uid': uid}) or []
								else:
									dom = eval(menu.action.params_store or '{}', {'uid': uid}).get('domain')
								# res[menu.id]['needaction_enabled'] = obj._needaction
								res[menu.id]['needaction_counter'] = obj._needaction_count(cr, uid, dom, context=context)
				else:
					res[menu.id]['needaction_counter'] = mixer_model.get(menu.id).get('default_count',0)
			else:
				if menu.action and menu.action.type in ('ir.actions.act_window', 'ir.actions.client') and menu.action.res_model:
					if menu.action.res_model in self.pool:
						obj = self.pool[menu.action.res_model]
						if obj._needaction:
							if menu.action.type == 'ir.actions.act_window':
								dom = menu.action.domain and eval(menu.action.domain, {'uid': uid}) or []
							else:
								dom = eval(menu.action.params_store or '{}', {'uid': uid}).get('domain')
							res[menu.id]['needaction_enabled'] = obj._needaction
							res[menu.id]['needaction_counter'] = obj._needaction_count(cr, uid, dom, context=context)
			# print "========>",menu.action," == ",menu.name, " : ",res[menu.id]
		return res
