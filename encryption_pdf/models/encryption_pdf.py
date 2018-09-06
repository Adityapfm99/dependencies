import cStringIO
from PyPDF2 import PdfFileWriter, PdfFileReader
from openerp import models, fields, api

class Report(models.Model):
	_inherit = 'report'

	def get_pdf(self, cr, uid, ids, report_name, html=None, data=None, context=None):
		result = super(Report, self).get_pdf(cr, uid, ids, report_name, html=html, data=data, context=context)

		if context.get('set_password',False):
			password = context.get('set_password')

			unencrypted_file = cStringIO.StringIO()
			unencrypted_file.write(result)

			# make a copy of the PDF file, and encrypt it
			pdf_file_reader = PdfFileReader(unencrypted_file)
			pdf_file_writer = PdfFileWriter()
			for page in pdf_file_reader.pages:
				pdf_file_writer.addPage(page)
			pdf_file_writer.encrypt(password)

			# write the encrypted payslip PDF content into a "memory file"
			encrypted_file = cStringIO.StringIO()
			pdf_file_writer.write(encrypted_file)
			unencrypted_file.close()

			result = encrypted_file.getvalue()

		return result
