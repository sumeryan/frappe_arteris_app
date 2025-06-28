// frappe.treeview_settings['Contract Item'] = {
//     title: __("Itens de Contrato"),
    
//     // Use o método padrão do Frappe primeiro para testar
//     get_tree_nodes: 'frappe.desk.treeview.get_children',
    
//     // Configurações para o método padrão
//     filters: [],
    
//     fields: [
//         {fieldtype: 'Data', fieldname: 'codigo', label: __('Código'), reqd: 1},
//         {fieldtype: 'Data', fieldname: 'descricao', label: __('Descrição'), reqd: 1},
//         {fieldtype: 'Float', fieldname: 'quantidade', label: __('Quantidade')},
//         {fieldtype: 'Currency', fieldname: 'valorunitario', label: __('Valor Unitário')},
//         {fieldtype: 'Check', fieldname: 'is_group', label: __('É Grupo')}
//     ],
    
//     // Campo pai para nested set
//     parent_field: "parent_contract_item",
    
//     // Campo de valor
//     value_field: "name",
    
//     breadcrumb: __("Contratos"),
    
//     get_label: function(node) {
//         if (node.data) {
//             return (node.data.codigo || '') + " - " + (node.data.descricao || '');
//         }
//         return node.value;
//     },
    
//     onload: function(treeview) {
//         // Adiciona filtro de contrato
//         const filter_wrapper = $('<div class="filter-wrapper">').appendTo(treeview.page.page_form);
        
//         const filter_field = frappe.ui.form.make_control({
//             parent: filter_wrapper,
//             df: {
//                 fieldtype: 'Link',
//                 fieldname: 'contrato',
//                 options: 'Contract',
//                 label: __('Filtrar por Contrato'),
//                 onchange: function() {
//                     const value = this.get_value();
//                     if (value) {
//                         treeview.filters = {"contrato": value};
//                     } else {
//                         treeview.filters = {};
//                     }
//                     treeview.make_tree();
//                 }
//             },
//             render_input: true
//         });
        
//         // Se veio com filtro na URL
//         if (frappe.route_options && frappe.route_options.contrato) {
//             filter_field.set_value(frappe.route_options.contrato);
//             treeview.filters = {"contrato": frappe.route_options.contrato};
//         }
//     },
    
//     toolbar: [
//         {
//             label: __("Adicionar Item"),
//             condition: function(node) {
//                 return node.expandable || node.is_root;
//             },
//             click: function(node) {
//                 let values = {
//                     is_group: 0
//                 };
                
//                 if (!node.is_root) {
//                     values.parent_contract_item = node.data.value;
                    
//                     // Herdar contrato do pai
//                     if (node.data && node.data.contrato) {
//                         values.contrato = node.data.contrato;
//                     }
//                 }
                
//                 frappe.new_doc("Contract Item", values);
//             }
//         }
//     ],
    
//     menu_items: [
//         {
//             label: __("Novo Item"),
//             action: function(node) {
//                 let values = {};
                
//                 if (node.data) {
//                     values.parent_contract_item = node.data.value || node.value;
//                     if (node.data.contrato) {
//                         values.contrato = node.data.contrato;
//                     }
//                 }
                
//                 frappe.new_doc('Contract Item', values);
//             },
//             condition: function(node) {
//                 return !node.is_root;
//             }
//         },
//         {
//             label: __('Editar'),
//             action: function(node) {
//                 frappe.set_route('Form', 'Contract Item', node.data.value || node.value);
//             },
//             condition: function(node) {
//                 return !node.is_root;
//             }
//         }
//     ]
// };