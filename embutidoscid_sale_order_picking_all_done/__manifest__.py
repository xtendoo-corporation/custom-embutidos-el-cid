###################################################################################
#
#    Xtendoo Technologies
#    Copyright (C) 2018-TODAY Xtendoo Technologies (<https://www.xtendoo.es>).
#    Author: Manuel Calero Solís(<https://www.xtendoo.es>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

{
    "name": "Sale Order Picking All Done",
    "summary": """Confirm, deliver and invoice sale orders in one click""",
    "version": "19.0.1.0.1",
    "description": """Confirm, deliver and invoice sale orders in one click.""",
    "author": "Manuel Calero Solís,",
    "company": "Xtendoo",
    "website": "https://xtendoo.es",
    "category": "Sales",
    "depends": ["sale_stock"],
    "license": "AGPL-3",
    "data": [
        "views/views.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
