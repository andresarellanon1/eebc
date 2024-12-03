
odoo.define('eebc_notices.TabChangeHandler', ['@web/views/form/form_controller'], function (require) {
    
    'use strict';

    const FormController = require('@web/views/form_controller');

    // const core = require('web.core');

    FormController.include({
        setup() {
            this._super(...arguments); // Llama al método original del controlador
            this.onTabChanged = this._onTabChanged.bind(this);
        },

        events: _.extend({}, FormController.prototype.events, {
            'click .o_notebook .nav-link': '_onTabChanged', // Detectar cambio de pestaña
        }),

        /**
         * Detectar el cambio de pestaña dentro del notebook
         */
        _onTabChanged: function (event) {
            const tab = $(event.target).attr('aria-controls');
            const tabName = tab === 'assign_tab' ? 'assign' : 'create';

            // Enviar el cambio al backend
            this.trigger_up('field_changed', {
                dataPointID: this.handle,
                changes: { active_tab: tabName },
            });

            console.log('Pestaña activa: ', tabName); // Mensaje de depuración
        },
    });
});