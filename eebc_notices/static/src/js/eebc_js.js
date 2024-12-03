
odoo.define('eebc_notices.TabChangeHandler', ['@web/views/form/form_controller'], function (require) {
    
    'use strict';

    const FormController = require('@web/views/form_controller');
    const { patch } = require('web.utils');


    // const core = require('web.core');

   // Extender FormController utilizando patch
   patch(FormController.prototype, 'eebc_notices.TabChangeHandler', {
    setup() {
        this._super(...arguments);
        this.onTabChanged = this._onTabChanged.bind(this); // Vincular método al controlador
    },

    /**
     * Detectar el cambio de pestaña dentro del notebook
     */
    _onTabChanged(event) {
        const tab = event.currentTarget.getAttribute('aria-controls');
        const tabName = tab === 'assign_tab' ? 'assign' : 'create';

        // Enviar el cambio al backend
        this.trigger_up('field_changed', {
            dataPointID: this.props.dataPointID,
            changes: { active_tab: tabName },
        });

        console.log('Pestaña activa: ', tabName); // Depuración
    },

    /**
     * Añadir evento personalizado al notebook
     */
    async start() {
        await this._super(...arguments);
        this.el.addEventListener('click', (event) => {
            if (event.target.classList.contains('nav-link')) {
                this._onTabChanged(event);
            }
        });
    },
});
});