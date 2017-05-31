from openerp import models, fields, api, _


class UserGuide(models.Model):
	_name="user.guide"


	def _name_get_resname(self, cr, uid, ids, object, method, context):
		data = {}
		for attachment in self.browse(cr, uid, ids, context=context):
			model_object = attachment.res_model
			res_id = attachment.res_id
			if model_object and res_id:
				model_pool = self.pool[model_object]
				res = model_pool.name_get(cr,uid,[res_id],context)
				res_name = res and res[0][1] or None
				if res_name:
					field = self._columns.get('res_name',False)
					if field and len(res_name) > field.size:
						res_name = res_name[:30] + '...' 
				data[attachment.id] = res_name or False
			else:
				data[attachment.id] = False
		return data

	def _storage(self, cr, uid, context=None):
		return self.pool['ir.config_parameter'].get_param(cr, SUPERUSER_ID, 'ir_attachment.location', 'file')

	def _filestore(self, cr, uid, context=None):
		return tools.config.filestore(cr.dbname)

	def force_storage(self, cr, uid, context=None):
		"""Force all attachments to be stored in the currently configured storage"""
		if not self.pool['res.users'].has_group(cr, uid, 'base.group_erp_manager'):
			raise AccessError(_('Only administrators can execute this action.'))

		location = self._storage(cr, uid, context)
		domain = {
			'db': [('store_fname', '!=', False)],
			'file': [('db_datas', '!=', False)],
		}[location]

		ids = self.search(cr, uid, domain, context=context)
		for attach in self.browse(cr, uid, ids, context=context):
			attach.write({'datas': attach.datas})
		return True

	# 'data' field implementation
	def _full_path(self, cr, uid, path):
		# sanitize ath
		path = re.sub('[.]', '', path)
		path = path.strip('/\\')
		return os.path.join(self._filestore(cr, uid), path)

	def _get_path(self, cr, uid, bin_data):
		sha = hashlib.sha1(bin_data).hexdigest()

		# retro compatibility
		fname = sha[:3] + '/' + sha
		full_path = self._full_path(cr, uid, fname)
		if os.path.isfile(full_path):
			return fname, full_path		# keep existing path

		# scatter files across 256 dirs
		# we use '/' in the db (even on windows)
		fname = sha[:2] + '/' + sha
		full_path = self._full_path(cr, uid, fname)
		dirname = os.path.dirname(full_path)
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
		return fname, full_path

	def _file_read(self, cr, uid, fname, bin_size=False):
		full_path = self._full_path(cr, uid, fname)
		r = ''
		try:
			if bin_size:
				r = os.path.getsize(full_path)
			else:
				r = open(full_path,'rb').read().encode('base64')
		except IOError:
			_logger.exception("_read_file reading %s", full_path)
		return r

	def _file_write(self, cr, uid, value):
		bin_value = value.decode('base64')
		fname, full_path = self._get_path(cr, uid, bin_value)
		if not os.path.exists(full_path):
			try:
				with open(full_path, 'wb') as fp:
					fp.write(bin_value)
			except IOError:
				_logger.exception("_file_write writing %s", full_path)
		return fname

	def _file_delete(self, cr, uid, fname):
		# using SQL to include files hidden through unlink or due to record rules
		cr.execute("SELECT COUNT(*) FROM ir_attachment WHERE store_fname = %s", (fname,))
		count = cr.fetchone()[0]
		full_path = self._full_path(cr, uid, fname)
		if not count and os.path.exists(full_path):
			try:
				os.unlink(full_path)
			except OSError:
				_logger.exception("_file_delete could not unlink %s", full_path)
			except IOError:
				# Harmless and needed for race conditions
				_logger.exception("_file_delete could not unlink %s", full_path)

	def _data_get(self, cr, uid, ids, name, arg, context=None):
		if context is None:
			context = {}
		result = {}
		bin_size = context.get('bin_size')
		for attach in self.browse(cr, uid, ids, context=context):
			if attach.store_fname:
				result[attach.id] = self._file_read(cr, uid, attach.store_fname, bin_size)
			else:
				result[attach.id] = attach.db_datas
		return result

	def _data_set(self, cr, uid, id, name, value, arg, context=None):
		# We dont handle setting data to null
		if not value:
			return True
		if context is None:
			context = {}
		location = self._storage(cr, uid, context)
		file_size = len(value.decode('base64'))
		attach = self.browse(cr, uid, id, context=context)
		fname_to_delete = attach.store_fname
		if location != 'db':
			fname = self._file_write(cr, uid, value)
			# SUPERUSER_ID as probably don't have write access, trigger during create
			super(ir_attachment, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size, 'db_datas': False}, context=context)
		else:
			super(ir_attachment, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size, 'store_fname': False}, context=context)

		# After de-referencing the file in the database, check whether we need
		# to garbage-collect it on the filesystem
		if fname_to_delete:
			self._file_delete(cr, uid, fname_to_delete)
		return True

	name = fields.Char("Name")
	department_id = fields.Many2one('hr.department',"Department")
	type_id = fields.Selection([('functional', 'Functional'), ('technical', 'Technical')])
	file_id = fields.Binary(_data_get, fnct_inv=_data_set, string='File Content', nodrop=True)
	description = fields.Text("Description")



