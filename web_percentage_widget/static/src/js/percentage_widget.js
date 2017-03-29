openerp.web_percentage_widget = function(instance) {
    var instance = openerp;
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    // form view
    instance.web.form.PercentageWidget = instance.web.form.FieldFloat.extend({
        display_name: _lt('PercentageWidget'),
        template: "PercentageWidget",
        render_value: function() {
            if (!this.get("effective_readonly")) {
                this._super();
            } else {
                var _value = parseFloat(this.get('value'));
                if (isNaN(_value)) {
                    this.$el.find(".percentage_filed").text('');
                }
                else{
                    this.$el.find(".percentage_filed").text((_value*100).toFixed(2) + '%');
                }
            }
        }
    });

    instance.web.form.widgets.add('percentage', 'instance.web.form.PercentageWidget');
    

    // list view
    instance.web.list.Percentage = instance.web.list.Column.extend({
        /**
         * Return a percentage format value
         *
         * @private
         */
        _format: function (row_data, options) {
            var _value = parseFloat(row_data[this.id].value);
            if (isNaN(_value)) {
                return null;
            }
            return (_value*100).toFixed(2) + '%';
        }
    });

    instance.web.list.columns.add('field.percentage', 'instance.web.list.Percentage');
    
};
