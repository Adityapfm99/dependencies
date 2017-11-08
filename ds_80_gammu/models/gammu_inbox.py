from openerp import tools
from openerp.osv import osv, fields
import re

class GammuInbox(osv.osv):
	_name = "gammu.inbox"
	_auto = False
	_rec_name = "ticket_nbr"

	def _compute_ticket(self,cr,uid,ids,field_names, args, context=None):
		res = dict([(i, {}) for i in ids])
		tickets = {}

		for inbox in self.browse(cr, uid, ids, context=context):
			reg = re.findall(r"#(\w+-\d{5})",inbox.textdecoded)
			res[inbox.id] = reg and reg[0] or "/"
		return res
	_columns = {
		"ticket_nbr"			: fields.function(_compute_ticket, string='Complete Name',type="char",readonly=True),
		"updatedindb"			: fields.datetime("Update Date",readonly=True),
		"receivingdatetime"		: fields.datetime("Received Date",readonly=True),
		"sendernumber"			: fields.char("Sender",readonly=True),
		"udh"					: fields.text("UDH",size=255,readonly=True),
		"classx"				: fields.integer("Class",readonly=True),
		"textdecoded"			: fields.text("Message",readonly=True),
		"recipientid"			: fields.text("Recipient ID",readonly=True),
		"smscnumber"			: fields.char("SMSCNumber",readonly=True),
		"processed"				: fields.boolean("Processed",readonly=True),
		"coding"				: fields.char("Coding",size=255,readonly=True),
		"text"					: fields.text("Encrypted Text",readonly=True),
		"inbox_id"				: fields.integer("Inbox DB ID",readonly=True),
	}

	_defaults = {
		"ticket_nbr":"/",
		"classx":-1,
		"textdecoded":"",
		"smscnumber":"",
		"processed":"",
		"coding":"Default_No_Compression",
		"text":"",
	}
	def init(self, cr):
		# self._table = account_invoice_report
		tools.drop_view_if_exists(cr, self._table)
		cr.execute("""CREATE or REPLACE VIEW %s as (select "ID" as inbox_id,
						min("ID") as id,
						"UpdatedInDB" as updatedindb,
						"ReceivingDateTime" as receivingdatetime,
						"Text" as text,
						"SenderNumber" as sendernumber,
						"Coding" as coding,
						"UDH" as udh,
						"SMSCNumber" as smscnumber,
						"Class" as classx,
						"TextDecoded" as textdecoded,
						"RecipientID" as recipientid,
						"Processed" as processed
						from inbox group by "ID")"""%(self._table)),