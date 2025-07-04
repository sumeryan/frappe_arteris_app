frappe.ui.form.on('Contract Measurement Note', {
    refresh(frm) {
        // Configurar query para campo item na tabela tabitem
        frm.fields_dict["tabitem"].grid.get_field("item").get_query = function(doc) {
            return {
                filters: {
                    'contrato': frm.doc.contrato,
                },
                no_create: 1,
                only_select: 1
            }
        }
    },
    
    setup: function(frm) {
        // Configurar query para campo pedidolinha na tabela tabsap
        frm.set_query("pedidolinha", "tabsap", function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            return {
                query: "arteris_app.arteris.doctype.contract_measurement_note.contract_measurement_note.get_sap_order_line",
                filters: {
                    'contrato': frm.doc.contrato || ''
                },
                no_create: 1,
                only_select: 1
            }
        });
        
        // Configurar query para campo funcao na tabela tabfuncoes
        frm.set_query("funcao", "tabfuncoes", function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            return {
                query: "arteris_app.arteris.doctype.contract_measurement_note.contract_measurement_note.get_work_role",
                filters: {
                    'contrato': frm.doc.contrato || ''
                },
                no_create: 1,
                only_select: 1
            }
        });

        // Query para campo item na tabela tabfuncoes
        frm.set_query("item", "tabfuncoes", function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            return {
                query: "arteris_app.arteris.doctype.contract_measurement_note.contract_measurement_note.get_work_role_item",
                filters: {
                    'contrato': frm.doc.contrato || '',
                    'funcao': row.funcao || ''
                },
                no_create: 1,
                only_select: 1
            }
        });     

        // Configurar query para campo funcao na tabela tabativos
        frm.set_query("ativo", "tabativos", function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            return {
                query: "arteris_app.arteris.doctype.contract_measurement_note.contract_measurement_note.get_asset",
                filters: {
                    'contrato': frm.doc.contrato || ''
                },
                no_create: 1,
                only_select: 1
            }
        });     
        
        // Configurar query para campo funcao na tabela tabativos
        frm.set_query("item", "tabativos", function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            return {
                query: "arteris_app.arteris.doctype.contract_measurement_note.contract_measurement_note.get_asset_item",
                filters: {
                    'contrato': frm.doc.contrato || '',
                    'ativo': row.ativo
                },
                no_create: 1,
                only_select: 1
            }
        });  
                
    },

    contrato: function(frm) {
        if (frm.doc.contrato) {
            frappe.call({
                method: "arteris_app.arteris.doctype.contract_measurement_note.contract_measurement_note.get_contract_data",
                args: {
                    contrato: frm.doc.contrato
                },
                callback: function(r) {
                    if (r.message) {
                        // Usar frm.set_value em vez de frm.doc direto
                        frm.set_value('subsidiaria', r.message['subsidiaria']);
                        frm.set_value('contratada', r.message['contratada']);
                        
                        // Forçar refresh dos campos após definir os valores
                        setTimeout(() => {
                            frm.refresh_field('subsidiaria');
                            frm.refresh_field('contratada');
                        }, 100);
                    }
                },
                error: function() {
                    frappe.msgprint('Erro ao buscar contrato');
                }
            });
        } else {
            // Limpar campos
            frm.set_value('subsidiaria', '');
            frm.set_value('contratada', '');
        }
    }    
});

// Eventos para a child table Contract Measurement Note SAP Order
frappe.ui.form.on('Contract Measurement Note SAP Order', {
    pedidolinha: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.pedidolinha) {
            frappe.call({
                method: "arteris_app.arteris.doctype.contract_measurement_note.contract_measurement_note.get_sap_order_line_cc",
                args: {
                    pedido_linha: row.pedidolinha
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'codigocc', r.message['codigocc']);
                    }
                },
                error: function() {
                    frappe.msgprint('Erro ao buscar centro de custo');
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, 'codigocc', '');
        }
    }
});

// Eventos para a child table Contract Measurement Note Work Role
frappe.ui.form.on('Contract Measurement Note Work Role', {
    // Evento quando o campo funcao muda
    item: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];       
        if (row.item && row.funcao) {
            // Chamar método do backend para obter dados da função e item
            frappe.call({
                method: "arteris_app.arteris.doctype.contract_measurement_note.contract_measurement_note.get_work_role_data",
                args: {
                    funcao: row.funcao,
                    item: row.item,
                    contrato: frm.doc.contrato
                },
                callback: function(r) {
                    if (r.message) {
                        // Setar os valores nos campos
                        frappe.model.set_value(cdt, cdn, 'valorporhora', r.message['valorporhora']);
                        frappe.model.set_value(cdt, cdn, 'valormensal', r.message['valormensal']);
                    }
                },
                error: function() {
                    frappe.msgprint('Erro ao buscar dados da função');
                }
            });
        } else if (!row.item) {
            // Limpar campos de valor quando item for removido
            frappe.model.set_value(cdt, cdn, 'valorporhora', '');
            frappe.model.set_value(cdt, cdn, 'valormensal', '');
        }
    },
    quantidade: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        calculate_valor_total(frm, cdt, cdn, row.valorporhora, row.valormensal);
    }
});

// Eventos para a child table Contract Measurement Note Asset
frappe.ui.form.on('Contract Measurement Note Asset', {
    item: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.ativo && row.item) {
            frappe.call({
                method: "arteris_app.arteris.doctype.contract_measurement_note.contract_measurement_note.get_asset_data",
                args: {
                    ativo: row.ativo, 
                    item: row.item,
                    contrato: frm.doc.contrato
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'valorunitario', r.message['valorunitario']);
                        frappe.model.set_value(cdt, cdn, 'valormensal', r.message['valormensal']);
                    }
                },
                error: function() {
                    frappe.msgprint('Erro ao buscar dados do ativo');
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, 'valorunitario', '');
            frappe.model.set_value(cdt, cdn, 'valormensal', '');
        }
    },
    quantidade: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        calculate_valor_total(frm, cdt, cdn, row.valorunitario, row.valormensal);
    }  
});

// Função para calcular valor total
function calculate_valor_total(frm, cdt, cdn, row_value_01, row_value_02) {
    let row = locals[cdt][cdn];
    
    // Só calcular se valortotal estiver vazio (sem dados)
    if (!row.valortotal || row.valortotal == 0) {
        let quantidade = flt(row.quantidade) || 0;
        let valor01 = flt(row_value_01) || 0;
        let valor02 = flt(row_value_02) || 0;
        let valor_total = 0;
        
        if (quantidade > 0) {
            // Priorizar valorunitario se não for zero
            if (valor01 != 0) {
                valor_total = quantidade * valor01;
            }
            // Caso contrário, usar valormensal se não for zero
            else if (valor02 != 0) {
                valor_total = quantidade * valor02;
            }
            
            // Definir o valor total calculado
            if (valor_total > 0) {
                frappe.model.set_value(cdt, cdn, 'valortotal', valor_total);
            }
        }
    }
}