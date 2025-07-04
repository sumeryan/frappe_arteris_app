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

    cw = frappe.db.get_value('Contract', contrato, 'contrato')

    print(f"DEBUG: Parâmetros recebidos - doctype: {doctype}, parent: {parent}, contrato: {contrato}, is_root: {is_root}")  # Debug
    
    # if is_root:
    #     # Para raiz, buscar itens sem parent (NULL ou vazio)
    #     filters.append(['parent_contract_item', 'is', 'not set'])
    # else:
    #     # Para nós filhos, buscar pelo parent específico
    #     filters.append(['parent_contract_item', '=', parent])

    if is_root:

        # Verfica qual item tem parents
        get_items = frappe.db

        base_query = """
            SELECT DISTINCT
                item.name,
                item.codigo,
                item.descricao,
                item.is_group,
                item.contrato,
                item.parent_contract_item
            FROM 
                `tabContract Item` item
            WHERE 
                item.parent_contract_item IS NULL
                AND item.is_group = 1
                AND item.contrato = %s
            LIMIT 1 
        """

        params = [contrato]
        
        children = frappe.db.sql(base_query, tuple(params), as_dict=True)
        
    # SEMPRE aplicar filtro de contrato quando fornecido
    else:
        # Para nós filhos, buscar pelo parent específico
        filters.append(['parent_contract_item', '=', parent])

        print(f"DEBUG: Buscando com filtros: {filters}")  # Debug
        
        # Buscar os registros com campos corretos
        children = frappe.get_all(
            doctype,
            filters=filters,
            fields=['name', 'codigo', 'descricao', 'is_group', 'contrato', 'parent_contract_item'],
            order_by='codigo, name'  # Ordenar por código primeiro
        )
    
    print(f"DEBUG: Encontrados {len(children)} registros")  # Debug
    
    # Formatar para tree view
    result = []
    for child in children:
        # Criar título combinando código e descrição
        # title_parts = []
        # if child.get('codigo'):
        #     title_parts.append(str(child.codigo))
        # if child.get('descricao'):
        #     title_parts.append(str(child.descricao))
        # title = ' - '.join(title_parts) if title_parts else child.name
        
        result.append({
            'id': child['name'],
            'title': child['descricao'],
            'value': child['name'],
            'expandable': child['is_group'],
            'is_group': child['is_group']
        })
    
    print(f"DEBUG: Resultado formatado: {result}")  # Debug
    return result

@frappe.whitelist()
def add_node(doctype, parent=None, **kwargs):
    """Método para adicionar novos nós na árvore"""
    # Extrair dados do kwargs
    codigo = kwargs.get('codigo')
    descricao = kwargs.get('descricao')
    contrato = kwargs.get('contrato')
    is_group = kwargs.get('is_group', 0)
    
    # Criar novo Contract Item
    doc = frappe.new_doc('Contract Item')
    doc.codigo = codigo
    doc.descricao = descricao
    doc.contrato = contrato
    doc.is_group = is_group
    doc.parent_contract_item = parent if parent else None
    
    doc.insert()
    
    return {
        'name': doc.name,
        'title': doc.descricao,
        'expandable': doc.is_group
    }

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

# import frappe
# from frappe.utils.nestedset import NestedSet

# class ContractItem(NestedSet):
#     pass

# @frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
# def get_sap_order_line(doctype, txt, searchfield, start, page_len, filters):
#     """
#     Busca linhas do pedido SAP específico
#     """
#     if isinstance(filters, str):
#         filters = json.loads(filters)
    
#     pedido_sap = filters.get('pedidosap', '')
    
#     # Se não tiver pedido_sap, retorna vazio
#     if not pedido_sap:
#         return []
    
#     return frappe.db.sql("""
#         SELECT DISTINCT
#             child.name,
#             child.name as description
#         FROM 
#             `tabSAP Order Period` child
#         WHERE 
#             child.parent = %(pedido_sap)s
#             AND child.name LIKE %(txt)s
#         ORDER BY 
#             child.idx, child.name
#         LIMIT %(start)s, %(page_len)s""", {
#         'pedido_sap': pedido_sap,
#         'txt': '%%%s%%' % txt,
#         'start': int(start),
#         'page_len': int(page_len)
#     })