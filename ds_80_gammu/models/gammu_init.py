from openerp import api, fields, models
import openerp.addons.decimal_precision as dp

class gammu_init(models.Model):
	_auto = False

	def init(self, cr):
		# self._table = account_invoice_report
		tools.drop_view_if_exists(cr, self._table)
		cr.execute("""
			CREATE OR REPLACE FUNCTION update_timestamp() RETURNS trigger AS $update_timestamp$
			  BEGIN
			    NEW."UpdatedInDB" := LOCALTIMESTAMP(0);
			    RETURN NEW;
			  END;
			$update_timestamp$ LANGUAGE plpgsql;

			CREATE TABLE daemons (
			  "Start" text NOT NULL,
			  "Info" text NOT NULL
			);

			CREATE TABLE gammu (
			  "Version" smallint NOT NULL DEFAULT '0'
			);

			INSERT INTO gammu ("Version") VALUES (15);

			CREATE TABLE inbox (
			  "UpdatedInDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
			  "ReceivingDateTime" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
			  "Text" text NOT NULL,
			  "SenderNumber" varchar(20) NOT NULL DEFAULT '',
			  "Coding" varchar(255) NOT NULL DEFAULT 'Default_No_Compression',
			  "UDH" text NOT NULL,
			  "SMSCNumber" varchar(20) NOT NULL DEFAULT '',
			  "Class" integer NOT NULL DEFAULT '-1',
			  "TextDecoded" text NOT NULL DEFAULT '',
			  "ID" serial PRIMARY KEY,
			  "RecipientID" text NOT NULL,
			  "Processed" boolean NOT NULL DEFAULT 'false',
			  CHECK ("Coding" IN 
			  ('Default_No_Compression','Unicode_No_Compression','8bit','Default_Compression','Unicode_Compression')) 
			);

			CREATE TRIGGER update_timestamp BEFORE UPDATE ON inbox FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

			CREATE TABLE outbox (
			  "UpdatedInDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
			  "InsertIntoDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
			  "SendingDateTime" timestamp NOT NULL DEFAULT LOCALTIMESTAMP(0),
			  "SendBefore" time NOT NULL DEFAULT '23:59:59',
			  "SendAfter" time NOT NULL DEFAULT '00:00:00',
			  "Text" text,
			  "DestinationNumber" varchar(20) NOT NULL DEFAULT '',
			  "Coding" varchar(255) NOT NULL DEFAULT 'Default_No_Compression',
			  "UDH" text,
			  "Class" integer DEFAULT '-1',
			  "TextDecoded" text NOT NULL DEFAULT '',
			  "ID" serial PRIMARY KEY,
			  "MultiPart" boolean NOT NULL DEFAULT 'false',
			  "RelativeValidity" integer DEFAULT '-1',
			  "SenderID" varchar(255),
			  "SendingTimeOut" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
			  "DeliveryReport" varchar(10) DEFAULT 'default',
			  "CreatorID" text NOT NULL,
			  "Retries" integer DEFAULT '0',
			  CHECK ("Coding" IN 
			  ('Default_No_Compression','Unicode_No_Compression','8bit','Default_Compression','Unicode_Compression')),
			  CHECK ("DeliveryReport" IN ('default','yes','no'))
			);

			CREATE INDEX outbox_date ON outbox("SendingDateTime", "SendingTimeOut");
			CREATE INDEX outbox_sender ON outbox("SenderID");


			CREATE TRIGGER update_timestamp BEFORE UPDATE ON outbox FOR EACH ROW EXECUTE PROCEDURE update_timestamp();


			CREATE TABLE outbox_multipart (
			  "Text" text,
			  "Coding" varchar(255) NOT NULL DEFAULT 'Default_No_Compression',
			  "UDH" text,
			  "Class" integer DEFAULT '-1',
			  "TextDecoded" text DEFAULT NULL,
			  "ID" serial,
			  "SequencePosition" integer NOT NULL DEFAULT '1',
			  PRIMARY KEY ("ID", "SequencePosition"),
			  CHECK ("Coding" IN 
			  ('Default_No_Compression','Unicode_No_Compression','8bit','Default_Compression','Unicode_Compression'))
			);

			CREATE TABLE pbk (
			  "ID" serial PRIMARY KEY,
			  "GroupID" integer NOT NULL DEFAULT '-1',
			  "Name" text NOT NULL,
			  "Number" text NOT NULL
			);


			CREATE TABLE pbk_groups (
			  "Name" text NOT NULL,
			  "ID" serial PRIMARY KEY
			);

			CREATE TABLE phones (
			  "ID" text NOT NULL,
			  "UpdatedInDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
			  "InsertIntoDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
			  "TimeOut" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
			  "Send" boolean NOT NULL DEFAULT 'no',
			  "Receive" boolean NOT NULL DEFAULT 'no',
			  "IMEI" varchar(35) PRIMARY KEY NOT NULL,
			  "NetCode" varchar(10) DEFAULT 'ERROR',
			  "NetName" varchar(35) DEFAULT 'ERROR',
			  "Client" text NOT NULL,
			  "Battery" integer NOT NULL DEFAULT -1,
			  "Signal" integer NOT NULL DEFAULT -1,
			  "Sent" integer NOT NULL DEFAULT 0,
			  "Received" integer NOT NULL DEFAULT 0
			);

			CREATE TRIGGER update_timestamp BEFORE UPDATE ON phones FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

			CREATE TABLE sentitems (
			  "UpdatedInDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
			  "InsertIntoDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
			  "SendingDateTime" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
			  "DeliveryDateTime" timestamp(0) WITHOUT time zone NULL,
			  "Text" text NOT NULL,
			  "DestinationNumber" varchar(20) NOT NULL DEFAULT '',
			  "Coding" varchar(255) NOT NULL DEFAULT 'Default_No_Compression',
			  "UDH" text NOT NULL,
			  "SMSCNumber" varchar(20) NOT NULL DEFAULT '',
			  "Class" integer NOT NULL DEFAULT '-1',
			  "TextDecoded" text NOT NULL DEFAULT '',
			  "ID" serial,
			  "SenderID" varchar(255) NOT NULL,
			  "SequencePosition" integer NOT NULL DEFAULT '1',
			  "Status" varchar(255) NOT NULL DEFAULT 'SendingOK',
			  "StatusError" integer NOT NULL DEFAULT '-1',
			  "TPMR" integer NOT NULL DEFAULT '-1',
			  "RelativeValidity" integer NOT NULL DEFAULT '-1',
			  "CreatorID" text NOT NULL,
			  CHECK ("Status" IN 
			  ('SendingOK','SendingOKNoReport','SendingError','DeliveryOK','DeliveryFailed','DeliveryPending',
			  'DeliveryUnknown','Error')),
			  CHECK ("Coding" IN 
			  ('Default_No_Compression','Unicode_No_Compression','8bit','Default_Compression','Unicode_Compression')),
			  PRIMARY KEY ("ID", "SequencePosition")
			);

			CREATE INDEX sentitems_date ON sentitems("DeliveryDateTime");
			CREATE INDEX sentitems_tpmr ON sentitems("TPMR");
			CREATE INDEX sentitems_dest ON sentitems("DestinationNumber");
			CREATE INDEX sentitems_sender ON sentitems("SenderID");

			CREATE TRIGGER update_timestamp BEFORE UPDATE ON sentitems FOR EACH ROW EXECUTE PROCEDURE update_timestamp();
			"""),