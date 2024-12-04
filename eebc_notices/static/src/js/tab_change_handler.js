odoo.define('eebc_notices.NoticeFileWizardController', [
    '@web/views/form/form_controller',
], function (require) {
    'use strict';

    const { FormController } = require('@web/views/form/form_controller');

    class NoticeFileWizardController extends FormController {
        setup() {
            super.setup(...arguments);
            console.log('Notice File Wizard Controller iniciado');
        }

        async start() {
            await super.start();
            console.log('Vista de modelo transitorio cargada correctamente');
            this.el.querySelectorAll('.o_notebook .nav-link').forEach((element) => {
                element.addEventListener('click', this._onTabChanged.bind(this));
            });
        }

        _onTabChanged(event) {
            const tab = event.currentTarget.getAttribute('aria-controls');
            const tabName = tab === 'assign_tab' ? 'assign' : 'create';

            console.log('Pestaña activa:', tabName);

            // Actualiza el backend con la pestaña activa
            this.trigger_up('field_changed', {
                dataPointID: this.props.dataPointID,
                changes: { active_tab: tabName },
            });
        }
    }

    return { NoticeFileWizardController };
});
