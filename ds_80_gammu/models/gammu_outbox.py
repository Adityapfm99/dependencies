from openerp import tools
from openerp.osv import osv, fields
from subprocess import Popen, PIPE
import math

class gammu_outbox(osv.osv):
	_name = "gammu.outbox"

	def _compute_text_type(self,cr,uid,ids,field_name,arg,context=None):
		if not context:context={}
		res = {}
		into_str_ids ="("
		for x in ids:
			into_str_ids+="'"+str(x)+"',"
		into_str_ids=into_str_ids[:-1]+")"

		queryob = """select "CreatorID" as outbox_id,"DeliveryReport" as status from outbox where "CreatorID" in """ + into_str_ids
		querysent = """select "CreatorID" as outbox_id,"Status" as status from sentitems where "CreatorID" in """ + into_str_ids
		cr.execute(queryob)
		qob = dict(cr.fetchall())
		cr.execute(querysent)
		qsent = dict(cr.fetchall())
		for outbox in self.browse(cr,uid,ids):
			res[outbox.id]={}
			res[outbox.id]['type']=len(outbox.message)>160 and 'long' or 'short'
			res[outbox.id]['len']=len(outbox.message)
			res[outbox.id]['state']= (str(outbox.id) in qob.keys() and qob[str(outbox.id)] and qob[str(outbox.id)].encode('utf8')) or \
									(str(outbox.id) in qsent.keys() and qsent[str(outbox.id)] and qsent[str(outbox.id)].encode('utf8')) or 'Sending'
									
		return res

	_columns ={
		"phone_id"		: fields.many2one("gammu.phone","Phone ID to sent the message"),
		"destination"	: fields.char("Phone Destination",required=True),
		"message"		: fields.text("Message",required=True),
		"type"			: fields.function(_compute_text_type,type="char",selection=[('short',"Short Message"),('long',"Long Message")],string="Text Type",multi="compute_size",store={'gammu.outbox': (lambda self, cr, uid, ids, c={}: ids, [], 10)}),
		"len"			: fields.function(_compute_text_type,type="integer",string="Text Length",multi="compute_size",
						store={'gammu.outbox': (lambda self, cr, uid, ids, c={}: ids, [], 10)}),
		'outbox'		: fields.integer("Outbox ID in table Outbox"),
		"state"			: fields.function(_compute_text_type,type="selection",
						selection=[
								('Sending',"In Process"),
								('SendingOK',"Sent with Report"),
								('SendingOKNoReport',"Sent No Report"),
								('DeliveryOK',"Delivery OK"),
								('DeliveryFailed',"Delivery Failed"),
								('DeliveryPending',"Delivery Pending"),
								('DeliveryUnknown',"Delivery Unknown"),
									],multi="compute_size",string="Status")
	}
	def generate_short_message(self,cr,uid,ids,outbox_id,message,destination,phone_id,multipart='f',context=None):
		if not context:context={}

		if context.get('UDH',False):
			query = """INSERT INTO outbox ("DestinationNumber","TextDecoded","CreatorID","Coding","Class","MultiPart","SenderID","UDH","RelativeValidity") VALUES 
				( '%s', '%s', '%s', 'Default_No_Compression',-1,'%s','%s','%s',255) RETURNING "ID";"""%(destination,message,outbox_id,multipart,phone_id,context.get('UDH'))

		else:
			query = """INSERT INTO outbox ("DestinationNumber","TextDecoded","CreatorID","Coding","Class","MultiPart","SenderID") VALUES 
				( '%s', '%s', '%s', 'Default_No_Compression',-1,'%s','%s') RETURNING "ID";"""%(destination,message.replace("'","''"),outbox_id,multipart,phone_id)

		cr.execute(query)
		res = cr.fetchone()
		res = res and res[0] or res
		self.pool.get('gammu.outbox').write(cr,uid,outbox_id,{'outbox':res})
		return res

	def generate_long_message(self,cr,uid,ids,outbox_id,message,destination,phone_id,multipart="t",context=None):
		if not context:context={}
		msg_length=len(message)
		nbr_of_msg = int(math.ceil(msg_length/153.0))
		part = {}
		for x in range(0,nbr_of_msg):
			part[x]=message[x*153:(x+1)*153]
		part_message=0
		for x in part.keys():
			UDH = '050003A7'+'{0:02x}'.format(int(nbr_of_msg))+'{0:02x}'.format(int(x+1))
			if x==0:
				context.update({'UDH':UDH})
				res = self.generate_short_message(cr,uid,ids,outbox_id,part[x].replace("'","''"),destination,phone_id,multipart='t',context=context)

				part_message = res
				self.pool.get('gammu.outbox').write(cr,uid,outbox_id,{'outbox':res})
			else:
				query = """INSERT INTO outbox_multipart ("SequencePosition","UDH","Class","TextDecoded","ID","Coding") VALUES 
						( %s, '%s', -1,'%s',%s,'Default_No_Compression') RETURNING "ID";"""%(x+1,UDH,part[x].replace("'","''"),part_message)
				cr.execute(query)
		return True

	def send_sms(self,cr,uid,ids,context=None):
		if not context:context={}
		
		# config_path = self.pool.get("gammu.phone").get_config_path(cr,uid,phone_id,destination,context)
		#gammu-smsd-inject -c /etc/gammu-smsdrc.conf TEXT 123456 -len 400 -text "All your base are belong to us"
		for outbox in self.browse(cr,uid,ids,context=context):
			if outbox.type=='short':
				self.generate_short_message(cr,uid,outbox.id,outbox.id,outbox.message,outbox.destination,outbox.phone_id.name,multipart='f',context=context)
			else:
				self.generate_long_message(cr,uid,outbox.id,outbox.id,outbox.message,outbox.destination,outbox.phone_id.name,multipart='t',context=context)
		return True
	
		