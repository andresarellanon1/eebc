odoo.define('eebc_notices.TabChangeHandler', [
    '@web/core/utils/patch', // Para aplicar parches a componentes OWL
    '@web/views/form/form_controller', // Para trabajar con FormController
], function (require) {
    'use strict';

    const { patch } = require('@web/core/utils/patch');
    const { FormController } = require('@web/views/form/form_controller');

    // Aplicar parche al prototipo de FormController
    patch(FormController.prototype, {
        /**
         * Configuración inicial al cargar el controlador
         */
        setup() {
            // Llamar al setup original mediante el super del componente
            FormController.prototype.setup.apply(this, arguments);

            // Inicializar la pestaña activa
            if (!this.env.activeTab) {
                this.env.activeTab = 'assign'; // Valor predeterminado
            }
        },

        /**
         * Detectar el cambio de pestaña
         * @param {Event} event
         */
        _onTabChanged(event) {
            const tab = event.currentTarget.getAttribute('aria-controls');
            const tabName = tab === 'assign_tab' ? 'assign' : 'create';

            // Actualizar la pestaña activa
            this.env.activeTab = tabName;

            // Depuración
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
            // Llamar al start original
            await FormController.prototype.start.apply(this, arguments);

            // Agregar listener de clic en las pestañas del notebook
            this.el.querySelectorAll('.o_notebook .nav-link').forEach((element) => {
                element.addEventListener('click', this._onTabChanged.bind(this));
            });
        },
    });
});
