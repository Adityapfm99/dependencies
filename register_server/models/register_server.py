from openerp import fields, models, api

class RegisterServer(models.Model):
    _name = 'register.server'
    
    url = fields.Char(string='URL')
    database_type = fields.Selection([('mysql','MySQL'),
    									('postgre','Postgre'),
    									('sqlserver','SQL Server')],string='Database Type')
    port = fields.Integer(string='Port')
    username = fields.Char(string='Username')
    password = fields.Char(string='Password',password=True)
