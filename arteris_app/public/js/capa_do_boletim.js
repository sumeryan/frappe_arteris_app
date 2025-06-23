frappe.pages['capa-do-boletim'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Capa do Boletim',
        single_column: true
    });

    frappe.call({
        method: 'your_app.path_to_controller.get_dados_boletim',
        args: { name: 'boletim_123' },
        callback: function(r) {
            if (r.message) {
                $(page.body).html(frappe.render_template("capa_do_boletim", {
                    doc: r.message
                }));
            }
        }
    });
};