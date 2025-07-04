frappe.treeview_settings['Contract Item'] = {
    breadcrumb: 'Arteris',
    title: __('Contract Items'),
    
    // Armazenar referência do treeview
    treeview: null,
    
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
    
    // Campos para novo nó
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
            reqd: true,
            hidden: 1  // Ocultar campo pois será preenchido automaticamente
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
        // Armazenar referência do treeview
        this.treeview = treeview;

        // Verificar query parameters
        var urlParams = new URLSearchParams(window.location.search);
        var contratoParam = urlParams.get('contrato');
        
        if (contratoParam) {
            setTimeout(function() {
                if (treeview.page && treeview.page.fields_dict && treeview.page.fields_dict.contrato) {
                    treeview.page.fields_dict.contrato.set_value(contratoParam);
                }
            }, 500);
        };

        // Injetar CSS para ocultar os IDs e o primeiro nó
        if (!document.getElementById('hide-tree-ids')) {
            var style = document.createElement('style');
            style.id = 'hide-tree-ids';
            style.innerHTML = `
                /* Ocultar spans com IDs na árvore */
                .tree-label span.text-muted {
                    display: none !important;
                }
                
                /* Ocultar o primeiro nó (raiz com UUID) */
                .tree.with-skeleton > .tree-link:first-child {
                    display: none !important;
                }
                
                /* Ajustar margem dos filhos para ficarem alinhados à esquerda */
                .tree.with-skeleton > ul {
                    margin-left: 0 !important;
                    padding-left: 0 !important;
                }
            `;
            document.head.appendChild(style);
        }        

        // Customizações adicionais ao carregar
        this.setup_dynamic_filtering(treeview);
        this.setup_add_node_handler(treeview);
    },
    
    // Configurar handler para adicionar nós
    setup_add_node_handler: function(treeview) {
        var me = this;
        
        // Sobrescrever o método de adicionar nó
        var original_add_click = treeview.add_click;
        
        treeview.add_click = function(node) {
            // Obter valor do filtro de contrato atual
            var contract_filter = me.get_contract_filter(treeview);
            
            if (!contract_filter) {
                frappe.msgprint(__('Por favor, selecione um contrato antes de adicionar itens'));
                return;
            }
            
            // Criar diálogo customizado
            var dialog = new frappe.ui.Dialog({
                title: __('Novo Item de Contrato'),
                fields: [
                    {
                        fieldtype: 'Check',
                        fieldname: 'is_group',
                        label: 'É Grupo? (Pasta que contem outros itens)',
                        default: 0
                    },                    
                    {
                        fieldtype: 'Data',
                        fieldname: 'codigo',
                        label: 'Código',
                        reqd: true
                    },
                    {
                        fieldtype: 'Data',
                        fieldname: 'descricao',
                        label: 'Descrição',
                        reqd: true
                    }
                ],
                primary_action_label: __('Adicionar'),
                primary_action: function(values) {
                    // Adicionar o contrato aos valores
                    values.contrato = contract_filter;
                    
                    // Chamar método para adicionar nó
                    frappe.call({
                        method: me.add_tree_node,
                        args: {
                            doctype: treeview.doctype,
                            parent: node ? node.data.value : null,
                            ...values
                        },
                        callback: function(r) {
                            if (r.message) {
                                dialog.hide();
                                
                                // Recarregar o nó pai ou a árvore
                                if (node) {
                                    node.reload();
                                } else {
                                    treeview.refresh();
                                }
                                
                                frappe.show_alert({
                                    message: __('Item adicionado com sucesso'),
                                    indicator: 'green'
                                });
                            }
                        }
                    });
                }
            });
            
            dialog.show();
        };
    },
    
    // Função auxiliar para obter o valor do filtro de contrato
    get_contract_filter: function(treeview) {
        var contract_filter = null;
        
        // Tentar várias formas de obter o filtro
        if (treeview.page && treeview.page.fields_dict && treeview.page.fields_dict.contrato) {
            contract_filter = treeview.page.fields_dict.contrato.get_value();
        } else if (treeview.filters && treeview.filters.contrato) {
            contract_filter = treeview.filters.contrato;
        } else if (treeview.page && treeview.page.sidebar) {
            var filter_field = treeview.page.sidebar.find('[data-fieldname="contrato"]');
            if (filter_field.length) {
                contract_filter = filter_field.val();
            }
        }
        
        return contract_filter;
    },
    
    // Função para configurar filtros dinâmicos
    setup_dynamic_filtering: function(treeview) {
        var me = this;
        
        // Sobrescrever o método get_children do treeview
        var original_get_children = treeview.get_children;
        
        treeview.get_children = function(node) {
            // Obter valor do filtro de contrato
            var contract_filter = me.get_contract_filter(treeview);
            
            console.log('Contract Filter:', contract_filter);
            console.log('Node:', node);
            
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