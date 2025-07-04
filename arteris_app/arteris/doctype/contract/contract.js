frappe.ui.form.on('Contract', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            // Adicionar ícone ao botão
            frm.add_custom_button(
                '<i class="fa fa-sitemap"></i> ' + __('Estrutura de Itens'), 
                function() {
                    // Navegar com query parameter
                    var route = frappe.get_route();
                    window.location.href = frappe.urllib.get_full_url(
                        `/app/contract-item?contrato=${encodeURIComponent(frm.doc.name)}`
                    );
                }
            ).addClass('btn-primary');
        }
    }
});