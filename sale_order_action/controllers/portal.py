
import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.sale.controllers.portal import CustomerPortal

# from odoo.addons.portal.controllers.portal import CustomerPortal
# from odoo.addons.portal.controllers.portal import CustomerPortal



import logging

_logger = logging.getLogger(__name__)


class CustomerPortalInherited(CustomerPortal):
    @http.route(['/my/orders/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_quote_accept(self, order_id, access_token=None, name=None, signature=None):
        # Aquí puedes agregar tu lógica personalizada antes o después
        # del código original.
        _logger.warning('AQUI ANDAMOS Y NO NOS VAMOS')
        # Llamar al método original si es necesario
        result = super(CustomerPortalInherited, self).portal_quote_accept(
            order_id, access_token, name, signature
        )

        # Modificar el comportamiento después de la llamada original si lo necesitas
        # Por ejemplo, agregar una nueva acción o registro adicional

        return result
    
    # @http.route(['/my/orders/<int:order_id>/accept'], type='json', auth="public", website=True)
    # def portal_quote_accept(self, order_id, access_token=None, name=None, signature=None):
        
    #     _logger.warning('ENTRAMOS A NUESTRO portal_quote_accept HEREDADOO')
    #     # get from query string if not on json param
    #     access_token = access_token or request.httprequest.args.get('access_token')
    #     try:
    #         order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
    #     except (AccessError, MissingError):
    #         return {'error': _('Invalid order.')}

    #     if not order_sudo._has_to_be_signed():
    #         return {'error': _('The order is not in a state requiring customer signature.')}
    #     if not signature:
    #         return {'error': _('Signature is missing.')}

    #     try:
    #         order_sudo.write({
    #             'signed_by': name,
    #             'signed_on': fields.Datetime.now(),
    #             'signature': signature,
    #         })
    #         request.env.cr.commit()
    #     except (TypeError, binascii.Error) as e:
    #         return {'error': _('Invalid signature data.')}

    #     if not order_sudo._has_to_be_paid():
    #         order_sudo.with_context(send_email=True).action_confirm()

    #     pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('sale.action_report_saleorder', [order_sudo.id])[0]

    #     _message_post_helper(
    #         'sale.order',
    #         order_sudo.id,
    #         _('Order signed by %s', name),
    #         attachments=[('%s.pdf' % order_sudo.name, pdf)],
    #         token=access_token,
    #     )

    #     query_string = '&message=sign_ok'
    #     if order_sudo._has_to_be_paid():
    #         query_string += '#allow_payment=yes'
    #     return {
    #         'force_refresh': True,
    #         'redirect_url': order_sudo.get_portal_url(query_string=query_string),
    #     }

