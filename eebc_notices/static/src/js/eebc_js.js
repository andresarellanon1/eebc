odoo.define('eebc_notices.TabChangeHandler', [
    'web.AbstractAction',
    'web.core'
], function (require) {
    'use strict';

    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');
    const _t = core._t;

    AbstractAction.include({
        events: _.extend({}, AbstractAction.prototype.events, {
            'click .o_notebook .nav-link': '_onTabChanged', // Evento para detectar cambio de pestaña
        }),

        _onTabChanged: function (event) {
            const tab = $(event.target).attr('aria-controls');
            const tabName = tab === 'assign_tab' ? 'assign' : 'create';

            this.trigger_up('field_changed', {
                dataPointID: this.handle,
                changes: { active_tab: tabName },
            });

            console.log('Pestaña activa: ', tabName); // Depuración
        },
    });
});
