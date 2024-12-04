odoo.define('eebc_notices.NoticeFileWizardController', [
    '@web/views/form/form_controller',
    '@web/views/form/form_view',
    '@web/views/form/form_renderer',
    '@web/core/registry',
], function (require) {
    'use strict';

    const { FormController } = require('@web/views/form/form_controller');
    const { FormView } = require('@web/views/form/form_view');
    const { FormRenderer } = require('@web/views/form/form_renderer');
    const { registry } = require('@web/core/registry');

    /**
     * Clase personalizada para el controlador del formulario
     */
    class NoticeFileWizardController extends FormController {
        setup() {
            console.log('Notice File Wizard Controller iniciado');
            super.setup(...arguments); // Llamar al setup original
        }
    }

    /**
     * Definición de la vista personalizada
     */
    const noticeWizardFormView = {
        ...FormView, // Extiende la vista del formulario original
        Controller: NoticeFileWizardController, // Usa el controlador personalizado
        Renderer: FormRenderer, // Usa el renderer original para la vista del formulario
    };

    // Registra la vista personalizada en el registro de vistas
    registry.category('views').add('noticeWizardFormViewTab', noticeWizardFormView);
});
