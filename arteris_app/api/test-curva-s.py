import frappe
from frappe import _

@frappe.whitelist()
def get_page():
    return {
        "title": _("Página Personalizada"),
        "content": get_page_content()
    }

def get_page_content():
    return """
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-12">
                <h3>Gerenciador de DocTypes</h3>
                <div class="form-group">
                    <label for="doctype-select">Selecionar DocType:</label>
                    <select id="doctype-select" class="form-control" style="width: 300px;">
                        <option value="">Selecione um DocType...</option>
                    </select>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-8">
                <div id="doctype-list-container" style="display: none;">
                    <h4>Itens do DocType</h4>
                    <div id="doctype-items" class="table-responsive">
                        <!-- Lista será carregada aqui -->
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div id="input-form" style="display: none;">
                    <h4>Adicionar Novo Item</h4>
                    <form id="new-item-form">
                        <div class="form-group">
                            <label for="item-name">Nome:</label>
                            <input type="text" id="item-name" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label for="item-description">Descrição:</label>
                            <textarea id="item-description" class="form-control" rows="3"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="item-data">Dados Adicionais:</label>
                            <input type="text" id="item-data" class="form-control">
                        </div>
                        <button type="submit" class="btn btn-primary">Adicionar Item</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    """

