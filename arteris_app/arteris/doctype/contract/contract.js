// frappe.ui.form.on('Contract', {
//     refresh: function(frm) {
//         if (!frm.is_new()) {
//             // Botão para ver árvore de itens
//             frm.add_custom_button(__('Árvore de Itens'), function() {
//                 frappe.route_options = {
//                     "contrato": frm.doc.name
//                 };
//                 frappe.set_route('Tree', 'Contract Item');
//             }, __('Visualizar'));
            
//             // Botão para criar item principal
//             frm.add_custom_button(__('Criar Item Principal'), function() {
//                 frappe.call({
//                     method: 'frappe.client.get_list',
//                     args: {
//                         doctype: 'Contract Item',
//                         filters: {
//                             contrato: frm.doc.name,
//                             is_group: 1,
//                             parent_contract_item: ["in", ["", null]]
//                         },
//                         limit: 1
//                     },
//                     callback: function(r) {
//                         if (r.message && r.message.length > 0) {
//                             frappe.msgprint({
//                                 title: __('Atenção'),
//                                 message: __('Este contrato já possui um item principal.'),
//                                 indicator: 'orange'
//                             });
                            
//                             frappe.confirm(
//                                 __('Deseja visualizar a árvore de itens?'),
//                                 function() {
//                                     frappe.route_options = {
//                                         "contrato": frm.doc.name
//                                     };
//                                     frappe.set_route('Tree', 'Contract Item');
//                                 }
//                             );
//                         } else {
//                             // Cria o item principal
//                             frappe.call({
//                                 // CAMINHO CORRETO DA API
//                                 method: 'arteris_app.api.contractitem.create_item_main',
//                                 args: {
//                                     contract: frm.doc.name
//                                 },
//                                 freeze: true,
//                                 freeze_message: __('Criando item principal...'),
//                                 callback: function(r) {
//                                     if (r.message) {
//                                         frappe.show_alert({
//                                             message: __('Item principal criado com sucesso!'),
//                                             indicator: 'green'
//                                         });
                                        
//                                         setTimeout(function() {
//                                             frappe.route_options = {
//                                                 "contrato": frm.doc.name
//                                             };
//                                             frappe.set_route('Tree', 'Contract Item');
//                                         }, 1000);
//                                     }
//                                 }
//                             });
//                         }
//                     }
//                 });
//             }, __('Ações'));
            
//             // Indicadores
//             frm.dashboard.add_indicator(
//                 __('Ver Itens'), 
//                 'blue'
//             ).on('click', function() {
//                 frappe.route_options = {
//                     "contrato": frm.doc.name
//                 };
//                 frappe.set_route('Tree', 'Contract Item');
//             });
            
//             // Estatísticas
//             frappe.call({
//                 method: 'frappe.client.get_list',
//                 args: {
//                     doctype: 'Contract Item',
//                     filters: {
//                         contrato: frm.doc.name
//                     },
//                     fields: ['count(name) as total']
//                 },
//                 callback: function(r) {
//                     if (r.message && r.message[0]) {
//                         frm.dashboard.add_indicator(
//                             __('Total de Itens: {0}', [r.message[0].total || 0]), 
//                             'blue'
//                         );
//                     }
//                 }
//             });
//         }
//     }
// });
