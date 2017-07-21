# -*- coding: utf-8 -*-
import logging
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp import tools
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect


class analytic_api(http.Controller):

	@http.route(['/api_analytic/',], type='http', auth="public")
	def api_analytic(self,**post):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		analytic_ids = pool.get('account.analytic.account').search(cr,SUPERUSER_ID,[('tag','=','gerai')])
		analytic = pool.get('account.analytic.account').browse(cr,SUPERUSER_ID,analytic_ids)
		result = []
		for aa in analytic:
			result.append({
				'id': aa.id,
				'nama_cabang': aa.name or '',
				'kode_cabang': aa.code or '',
				'nama_kota'	 : aa.parent_id and aa.parent_id.name or '',
				'kode_kota'	 : aa.parent_id and aa.parent_id.code or '',
				'nama_provinsi': aa.parent_id and aa.parent_id.parent_id and aa.parent_id.parent_id.name or '',
				'kode_provinsi': aa.parent_id and aa.parent_id.parent_id and aa.parent_id.parent_id.code or '',
				})
		print "===================",str(result)
		return str(result)