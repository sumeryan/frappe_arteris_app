// // ==================================================
// // FORM SCRIPT CONTRACT ITEM - contract_item.js
// // ==================================================

// frappe.ui.form.on('Contract Item', {
//     refresh: function(frm) {
//         // Filtro para parent baseado no contrato
//         frm.set_query('parent_contract_item', function() {
//             if (!frm.doc.contrato) {
//                 return {
//                     filters: {
//                         'name': 'valor_impossivel'
//                     }
//                 };
//             }
            
//             return {
//                 filters: {
//                     'contrato': frm.doc.contrato,
//                     'is_group': 1,
//                     'name': ['!=', frm.doc.name || 'new']
//                 }
//             };
//         });
        
//         // Botão para voltar à tree
//         if (frm.doc.contrato) {
//             frm.add_custom_button(__('🌳 Ver Estrutura'), function() {
//                 let url = `/app/tree/Contract Item?contrato=${encodeURIComponent(frm.doc.contrato)}`;
//                 window.location.href = url;
//             }, __('Navegação'));
//         }
        
//         // Validar se tem contrato
//         if (!frm.doc.contrato && !frm.is_new()) {
//             frm.set_intro(__('⚠️ Este item não está vinculado a nenhum contrato!'), 'red');
//         }
//     },
    
//     onload: function(frm) {
//         // Auto-preencher contrato se vier de route
//         if (frappe.route_options && frm.is_new()) {
//             if (frappe.route_options.contrato) {
//                 frm.set_value('contrato', frappe.route_options.contrato);
//             }
//             frappe.route_options = {};
//         }
//     },
    
//     validate: function(frm) {
//         // Validação obrigatória do contrato
//         if (!frm.doc.contrato) {
//             frappe.validated = false;
//             frappe.throw(__('Campo Contrato é obrigatório'));
//         }
//     }
// });