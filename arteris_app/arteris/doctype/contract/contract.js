// // ==================================================
// // BOTÃO NO CONTRACT - contract.js
// // ==================================================

// frappe.ui.form.on('Contract', {
//     refresh: function(frm) {
//         if (!frm.is_new()) {
//             frm.add_custom_button(__('🌳 Ver Estrutura'), function() {
//                 abrirTreeComFiltro(frm);
//             }, __('Ações'));
            
//             frm.add_custom_button(__('➕ Criar Item Raiz'), function() {
//                 criarItemRaiz(frm);
//             }, __('Ações'));
//         }
//     }
// });

// function abrirTreeComFiltro(frm) {
//     // Método 1: URL com parâmetro
//     let url = `/app/tree/Contract Item?contrato=${encodeURIComponent(frm.doc.name)}`;
//     window.location.href = url;
// }

// function criarItemRaiz(frm) {
//     let codigo = 'Contrato ' + (frm.doc.contrato || frm.doc.name);
    
//     frappe.call({
//         method: 'frappe.client.insert',
//         args: {
//             doc: {
//                 doctype: 'Contract Item',
//                 codigo: codigo,
//                 descricao: codigo,
//                 contrato: frm.doc.name,
//                 is_group: 1,
//                 parent_contract_item: null,
//                 quantidade: 1,
//                 valorunitario: 0
//             }
//         },
//         callback: function(r) {
//             if (r.message) {
//                 frappe.show_alert({
//                     message: __('Item raiz criado!'),
//                     indicator: 'green'
//                 }, 3);
                
//                 // Abrir tree view atualizada
//                 abrirTreeComFiltro(frm);
//             }
//         }
//     });
// }
