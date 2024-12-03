odoo.define('eebc_notices.TabChangeHandler', function (require) {
    'use strict';

    const FormController = require('web.FormController');
    const core = require('web.core');
    const _t = core._t;

    FormController.include({
        events: _.extend({}, FormController.prototype.events, {
            'click .o_notebook .nav-link': '_onTabChanged',
        }),

        _onTabChanged: function (event) {
            const tab = $(event.target).attr('aria-controls');
            const tabName = tab === 'assign_tab' ? 'assign' : 'create';

            this.trigger_up('field_changed', {
                dataPointID: this.handle,
                changes: { active_tab: tabName },
            });
        },
    });
});