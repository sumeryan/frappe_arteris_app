import frappe
from frappe.utils.nestedset import NestedSet

class ContractItem(NestedSet):
    nsm_parent_field = "parent_contract_item"
    
    def on_update(self):
        NestedSet.on_update(self)
    
    def on_trash(self):
        NestedSet.validate_if_child_exists(self)
        NestedSet.on_trash(self)

@frappe.whitelist()
def get_children(doctype, parent="", contrato=None, is_root=False):
    """
    Retorna os filhos de um nó específico com filtro opcional por contrato
    """
    filters = []
    
    if is_root:
        filters.append(['parent_contract_item', '=', ''])
    else:
        filters.append(['parent_contract_item', '=', parent])
    
    # Aplicar filtro de contrato se fornecido
    if contrato:
        filters.append(['contrato', '=', contrato])
    
    # Buscar os registros com campos corretos
    children = frappe.get_all(
        doctype,
        filters=filters,
        fields=['name', 'codigo', 'descricao', 'is_group', 'contrato', 'parent_contract_item'],
        order_by='name'
    )
    
    # Formatar para tree view
    result = []
    for child in children:
        # Criar título combinando código e descrição
        title_parts = []
        if child.get('codigo'):
            title_parts.append(child.codigo)
        if child.get('descricao'):
            title_parts.append(child.descricao)
        title = ' - '.join(title_parts) if title_parts else child.name
        
        result.append({
            'id': child.name,
            'title': title,
            'value': child.name,
            'expandable': child.is_group,
            'is_group': child.is_group
        })
    
    return result

@frappe.whitelist()
def add_node():
    """Método para adicionar novos nós na árvore"""
    return True

@frappe.whitelist()
def get_contract_item_tree(contract_id):
    """
    Retorna estrutura hierárquica completa para um contrato específico
    """
    items = frappe.get_all(
        'Contract Item',
        filters={'contrato': contract_id},
        fields=['name', 'codigo', 'descricao', 'parent_contract_item', 'is_group', 'lft', 'rgt'],
        order_by='lft'
    )
    
    # Construir árvore hierárquica
    tree = build_tree_structure(items)
    return tree

def build_tree_structure(items):
    """
    Constrói estrutura de árvore a partir de lista flat
    """
    tree = []
    item_map = {item['name']: item for item in items}
    
    for item in items:
        item['children'] = []
        parent = item.get('parent_contract_item')
        
        if parent and parent in item_map:
            item_map[parent]['children'].append(item)
        else:
            tree.append(item)
    
    return tree