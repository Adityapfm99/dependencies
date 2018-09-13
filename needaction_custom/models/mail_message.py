from openerp.osv import osv, fields

class mail_message(osv.Model):
	""" Messages model: system notification (replacing res.log notifications),
		comments (OpenChatter discussion) and incoming emails. """
	_inherit = 'mail.message'

	def _needaction_count(self, cr, uid, domain=None, context=None):
		return 0

	def _needaction_domain_get(self, cr, uid, context=None):
		return False