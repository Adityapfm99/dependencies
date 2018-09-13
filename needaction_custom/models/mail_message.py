from openerp.osv import osv,fields

class mail_message(osv.Model):
	""" Messages model: system notification (replacing res.log notifications),
		comments (OpenChatter discussion) and incoming emails. """
	_inherit = 'mail.message'

	def _needaction_count(self, cr, uid, domain=None, context=None):
		res = super(mail_message,self)._needaction_count(cr, uid, context=context)
		return 0

	def _needaction_domain_get(self, cr, uid, context=None):
		res = super(mail_message,self)._needaction_domain_get(cr, uid, context=context)

		return False