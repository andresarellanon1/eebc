odoo.define('eebc_notices.TabChangeHandler', [
    '@web/core/utils/patch', // Para extender el controlador con patch
    '@web/views/form/form_controller', // Para extender FormController
], function (require) {
    'use strict';

    const { patch } = require('@web/core/utils/patch');
    const { FormController } = require('@web/views/form/form_controller');

    // Aplicar patch al prototipo de FormController
    patch(FormController.prototype, 'eebc_notices.TabChangeHandler', {
        /**
         * Configuración inicial al cargar el controlador
         */
        setup() {
            // Llamar al método original
            this._super(...arguments);

            // Agregar un entorno adicional si es necesario
            this.env.activeTab = 'assign'; // Valor predeterminado
        },

        /**
         * Detectar el cambio de pestaña
         * @param {Event} event
         */
        _onTabChanged(event) {
            const tab = event.currentTarget.getAttribute('aria-controls');
            const tabName = tab === 'assign_tab' ? 'assign' : 'create';

            // Actualizar el entorno con la pestaña activa
            this.env.activeTab = tabName;

            // Depuración en la consola
            console.log('Pestaña activa:', tabName);

            // Enviar el cambio al backend
            this.trigger_up('field_changed', {
                dataPointID: this.props.dataPointID,
                changes: { active_tab: tabName },
            });
        },

        /**
         * Agregar evento personalizado al cargar el DOM
         */
        async start() {
            await this._super(...arguments);
            // Agregar el listener para detectar el cambio de pestañas
            this.el.querySelectorAll('.o_notebook .nav-link').forEach((element) => {
                element.addEventListener('click', this._onTabChanged.bind(this));
            });
        },
    });
});
