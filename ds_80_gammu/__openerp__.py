# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Dedi Sinaga.
#    @author: - Dedi Sinaga <http://dedisinaga.blogspot.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Gammu SMSD",

    'summary': "Gammu SMSD - SMS Gateway",

    'description': """
========================
Gammu SMS Gateway
========================

    """,

    'author': 'Dedi Sinaga',
    'website': "https://github.com/dedisinaga/",
    'category': 'Technical',
    'sequence': 3,
    'version': '8.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
    ],

    # always loaded
    'data': [
        'security/ds_80_gammu_security.xml',
        'security/ir.model.access.csv',
        "views/gammu_inbox_view.xml",
        "views/gammu_phone_view.xml",
        "views/gammu_outbox_view.xml",
        ],
    # only loaded in demonstration mode
    'demo': [],
    'images': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}