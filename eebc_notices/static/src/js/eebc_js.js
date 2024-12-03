odoo.define('eebc_notices.TabChangeHandler', [
    '@web/views/form/form_controller',
], function (require) {
    'use strict';

    const { FormController } = require('@web/views/form/form_controller');

    /**
     * Clase personalizada para el controlador del formulario
     */
    class NoticeFormController extends FormController {
        /**
         * Configuración inicial al cargar el controlador
         */
        setup() {
            super.setup(...arguments); // Llamar al setup del controlador base

            // Inicializar pestaña activa
            this.env.activeTab = 'assign';
        }

        /**
         * Detectar el cambio de pestaña
         * @param {Event} event
         */
        _onTabChanged(event) {
            const tab = event.currentTarget.getAttribute('aria-controls');
            const tabName = tab === 'assign_tab' ? 'assign' : 'create';

            // Actualizar la pestaña activa en el entorno
            this.env.activeTab = tabName;

            // Depuración
            console.log('Pestaña activa:', tabName);

            // Enviar el cambio al backend
            this.trigger_up('field_changed', {
                dataPointID: this.props.dataPointID,
                changes: { active_tab: tabName },
            });
        }

        /**
         * Agregar evento personalizado al cargar el DOM
         */
        async start() {
            await super.start(); // Llamar al método original

            // Agregar evento click a las pestañas del notebook
            this.el.querySelectorAll('.o_notebook .nav-link').forEach((element) => {
                element.addEventListener('click', this._onTabChanged.bind(this));
            });
        }
    }

    return { NoticeFormController };
});
