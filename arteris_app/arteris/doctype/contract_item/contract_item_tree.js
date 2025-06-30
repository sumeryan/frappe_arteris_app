frappe.treeview_settings['Contract Item'] = {
    breadcrumb: 'Arteris',
    title: __('Contract Items'),
    
    // Configuração dos filtros
    filters: [
        {
            fieldname: 'contrato',
            fieldtype: 'Link',
            options: 'Contract',
            label: __('Contract'),
            on_change: function() {
                // Recarregar árvore quando contrato mudar
                this.refresh();
            }
        }
    ],
    
    // Método para obter nós da árvore
    get_tree_nodes: 'arteris_app.arteris.doctype.contract_item.contract_item.get_children',
    
    // Método para adicionar nós
    add_tree_node: 'arteris_app.arteris.doctype.contract_item.contract_item.add_node',
    
    // Campos para novo nó (corrigidos para usar campos existentes)
    fields: [
        {
            fieldtype: 'Data',
            fieldname: 'codigo',
            label: __('Code'),
            reqd: true
        },
        {
            fieldtype: 'Data',
            fieldname: 'descricao',
            label: __('Description'),
            reqd: true
        },
        {
            fieldtype: 'Link',
            fieldname: 'contrato',
            options: 'Contract',
            label: __('Contract'),
            reqd: true
        },
        {
            fieldtype: 'Check',
            fieldname: 'is_group',
            label: __('Is Group')
        }
    ],
    
    // Campos a ignorar
    ignore_fields: ['parent_contract_item'],
    
    // Configuração adicional
    root_label: 'All Contract Items',
    get_tree_root: false,
    
    // Evento ao carregar
    onload: function(treeview) {
        // Customizações adicionais ao carregar
        this.setup_dynamic_filtering(treeview);
    },
    
    // Função para configurar filtros dinâmicos (método simplificado)
    setup_dynamic_filtering: function(treeview) {
        var me = this;
        
        // Sobrescrever o método get_children do treeview
        var original_get_children = treeview.get_children;
        
        treeview.get_children = function(node) {
            // Obter valor do filtro de contrato
            var contract_filter = null;
            if (treeview.page && treeview.page.sidebar) {
                var filter_field = treeview.page.sidebar.find('[data-fieldname="contrato"]');
                if (filter_field.length) {
                    contract_filter = filter_field.val();
                }
            }
            
            return frappe.call({
                method: me.get_tree_nodes,
                args: {
                    doctype: treeview.doctype,
                    parent: node ? node.data.value : '',
                    contrato: contract_filter || null,
                    is_root: !node
                },
                callback: function(r) {
                    if (r.message) {
                        if (node) {
                            node.load_children(r.message);
                        } else {
                            treeview.load_children(r.message);
                        }
                    }
                }
            });
        };
    }
};