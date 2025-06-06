frappe.pages['custom-page'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Página Personalizada',
        single_column: true
    });

    // Inicializar a página
    init_custom_page(page);
};

function init_custom_page(page) {
    // Carregar lista de DocTypes disponíveis
    load_doctypes();
    
    // Event listener para mudança do dropdown
    $('#doctype-select').on('change', function() {
        const selected_doctype = $(this).val();
        if (selected_doctype) {
            load_doctype_items(selected_doctype);
            $('#doctype-list-container').show();
            $('#input-form').show();
        } else {
            $('#doctype-list-container').hide();
            $('#input-form').hide();
        }
    });
    
    // Event listener para o formulário
    $('#new-item-form').on('submit', function(e) {
        e.preventDefault();
        add_new_item();
    });
}

function load_doctypes() {
    frappe.call({
        method: 'frappe.desk.search.search_link',
        args: {
            doctype: 'DocType',
            txt: '',
            filters: {
                'istable': 0,
                'issingle': 0,
                'custom': 0
            }
        },
        callback: function(r) {
            if (r.message) {
                const select = $('#doctype-select');
                select.empty().append('<option value="">Selecione um DocType...</option>');
                
                r.message.forEach(function(item) {
                    select.append(`<option value="${item.value}">${item.value}</option>`);
                });
            }
        }
    });
}

function load_doctype_items(doctype) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: doctype,
            fields: ['name', 'creation', 'modified'],
            limit_page_length: 20,
            order_by: 'creation desc'
        },
        callback: function(r) {
            if (r.message) {
                render_doctype_items(r.message, doctype);
            }
        }
    });
}

function render_doctype_items(items, doctype) {
    let html = `
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Nome</th>
                    <th>Criado em</th>
                    <th>Modificado em</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    items.forEach(function(item) {
        html += `
            <tr>
                <td><a href="/app/${doctype.toLowerCase()}/${item.name}" target="_blank">${item.name}</a></td>
                <td>${frappe.datetime.str_to_user(item.creation)}</td>
                <td>${frappe.datetime.str_to_user(item.modified)}</td>
                <td>
                    <button class="btn btn-sm btn-info" onclick="view_related_docs('${doctype}', '${item.name}')">
                        Ver Relacionados
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    $('#doctype-items').html(html);
}

function view_related_docs(doctype, doc_name) {
    // Buscar documentos relacionados
    frappe.call({
        method: 'your_app.api.get_related_documents',
        args: {
            doctype: doctype,
            doc_name: doc_name
        },
        callback: function(r) {
            if (r.message) {
                show_related_docs_modal(r.message);
            }
        }
    });
}

function show_related_docs_modal(related_docs) {
    const dialog = new frappe.ui.Dialog({
        title: 'Documentos Relacionados',
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'related_docs_html'
            }
        ]
    });
    
    let html = '<div class="related-docs-container">';
    
    Object.keys(related_docs).forEach(function(doctype) {
        html += `<h5>${doctype}</h5>`;
        html += '<ul>';
        related_docs[doctype].forEach(function(doc) {
            html += `<li><a href="/app/${doctype.toLowerCase()}/${doc.name}" target="_blank">${doc.name}</a></li>`;
        });
        html += '</ul>';
    });
    
    html += '</div>';
    
    dialog.fields_dict.related_docs_html.$wrapper.html(html);
    dialog.show();
}

function add_new_item() {
    const selected_doctype = $('#doctype-select').val();
    const name = $('#item-name').val();
    const description = $('#item-description').val();
    const additional_data = $('#item-data').val();
    
    if (!selected_doctype || !name) {
        frappe.msgprint('Por favor, selecione um DocType e preencha o nome.');
        return;
    }
    
    // Criar novo documento
    frappe.call({
        method: 'frappe.client.insert',
        args: {
            doc: {
                doctype: 'Custom Data Table', // Substitua pelo seu DocType personalizado
                doctype_reference: selected_doctype,
                item_name: name,
                description: description,
                additional_data: additional_data
            }
        },
        callback: function(r) {
            if (r.message) {
                frappe.msgprint('Item adicionado com sucesso!');
                $('#new-item-form')[0].reset();
                // Recarregar a lista se necessário
                load_doctype_items(selected_doctype);
            }
        }
    });
}

// 2. JavaScript para a página (arquivo: custom_page.js)


// 3. Método Python para buscar documentos relacionados (arquivo: api.py)


// 4. Criar DocType para armazenar os dados personalizados
// Nome: Custom Data Table
// Campos:
// - doctype_reference (Link para DocType)
// - item_name (Data)
// - description (Text)
// - additional_data (Data)
// - creation (Datetime)
// - modified (Datetime)