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
            console.log('Inicio del setup en NoticeFormController'); // Depuración inicial
            super.setup(...arguments); // Llamar al setup del controlador base

            // Inicializar pestaña activa
            this.env.activeTab = 'assign';
            console.log('Pestaña activa inicializada como:', this.env.activeTab); // Validación de inicialización
        }

        /**
         * Detectar el cambio de pestaña
         * @param {Event} event
         */
        _onTabChanged(event) {
            console.log('Evento de cambio de pestaña detectado'); // Confirmación del evento

            const tab = event.currentTarget.getAttribute('aria-controls');
            const tabName = tab === 'assign_tab' ? 'assign' : 'create';

            console.log('Tab detectado:', tab, 'Tab Name:', tabName); // Validar valores del atributo y nombre de pestaña

            // Actualizar la pestaña activa en el entorno
            this.env.activeTab = tabName;
            console.log('Pestaña activa actualizada a:', this.env.activeTab); // Confirmación de actualización

            // Enviar el cambio al backend
            this.trigger_up('field_changed', {
                dataPointID: this.props.dataPointID,
                changes: { active_tab: tabName },
            });
            console.log('Cambio de pestaña enviado al backend'); // Confirmación del envío
        }

        /**
         * Agregar evento personalizado al cargar el DOM
         */
        async start() {
            console.log('Inicio del método start en NoticeFormController'); // Depuración inicial
            await super.start(); // Llamar al método original
            console.log('Método start del controlador base completado'); // Confirmación de la ejecución del método base

            // Agregar evento click a las pestañas del notebook
            this.el.querySelectorAll('.o_notebook .nav-link').forEach((element) => {
                console.log('Agregando listener de clic para:', element); // Validar los elementos detectados
                element.addEventListener('click', this._onTabChanged.bind(this));
            });
            console.log('Listeners de clic agregados a las pestañas del notebook'); // Confirmación final
        }
    }

    return { NoticeFormController };
});
