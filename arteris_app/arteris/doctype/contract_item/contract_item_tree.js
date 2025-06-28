// // ==================================================
// // VERSÃO SIMPLIFICADA - contract_item_tree.js
// // ==================================================

// frappe.provide('frappe.treeview_settings');

// frappe.treeview_settings['Contract Item'] = {
//     breadcrumb: 'Contratos',
//     title: __('Estrutura de Itens do Contrato'),
    
//     // Configurações básicas
//     root_label: 'Todos os Itens',
//     get_tree_root: false,
    
//     // Filtros da tree
//     filters: [
//         {
//             fieldname: 'contrato',
//             fieldtype: 'Link',
//             options: 'Contract',
//             label: __('Contrato'),
//             onchange: function() {
//                 const tree = frappe.views.trees['Contract Item'];
//                 if (tree && tree.tree) {
//                     tree.tree.refresh();
//                 }
//             }
//         }
//     ],
    
//     // Método para buscar nós - DEVE ser um caminho Python
//     get_tree_nodes: 'arteris.arteris.custom.contract_item_tree.get_tree_nodes',
    
//     // Campos a exibir
//     fields: [
//         {fieldtype: 'Link', fieldname: 'contrato', label: __('Contrato'), options: 'Contract'},
//         {fieldtype: 'Data', fieldname: 'codigo', label: __('Código')},
//         {fieldtype: 'Data', fieldname: 'descricao', label: __('Descrição')},
//         {fieldtype: 'Check', fieldname: 'is_group', label: __('É Grupo')}
//     ],
    
//     // Ações do menu de contexto
//     menu_items: [
//         {
//             label: __('Novo'),
//             action: function(node, btn) {
//                 frappe.new_doc('Contract Item', {
//                     parent_contract_item: node.label !== 'Todos os Itens' ? node.value : null
//                 });
//             }
//         }
//     ],
    
//     // Evento ao carregar
//     onload: function(treeview) {
//         // Verificar parâmetro na URL
//         const urlParams = new URLSearchParams(window.location.search);
//         const contratoParam = urlParams.get('contrato');
        
//         if (contratoParam && treeview.page) {
//             setTimeout(() => {
//                 const field = treeview.page.fields_dict.contrato;
//                 if (field) {
//                     field.set_value(contratoParam);
//                 }
//             }, 500);
//         }
//     },
    
//     // Estender argumentos para incluir filtro
//     extend_toolbar: false,
    
//     // Callback antes de renderizar
//     before_render: function() {
//         // Adicionar filtro de contrato aos argumentos
//         const contrato = cur_page.fields_dict.contrato?.get_value();
//         if (contrato) {
//             this.args = {contrato: contrato};
//         }
//     }
// };

// // ==================================================
// // ALTERNATIVA: Monkey patch para passar filtros
// // ==================================================

// frappe.ready(() => {
//     // Interceptar TreeView para Contract Item
//     const original_make_tree = frappe.views.TreeView.prototype.make_tree;
    
//     frappe.views.TreeView.prototype.make_tree = function() {
//         if (this.doctype === 'Contract Item') {
//             // Adicionar método para obter argumentos extras
//             this.get_args = function() {
//                 const args = {};
//                 const contrato = this.page.fields_dict.contrato?.get_value();
//                 if (contrato) {
//                     args.contrato = contrato;
//                 }
//                 return args;
//             };
//         }
        
//         // Chamar método original
//         return original_make_tree.apply(this, arguments);
//     };
// });