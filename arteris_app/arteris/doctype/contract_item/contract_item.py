# # -*- coding: utf-8 -*-
# """
# Arquivo: arteris/arteris/custom/contract_item_tree.py
# Métodos customizados para a Tree View do Contract Item
# """

# import frappe
# from frappe import _

# @frappe.whitelist()
# def get_tree_nodes(parent=None, contrato=None):
#     """
#     Retorna os nós da árvore para Contract Item
    
#     Args:
#         parent: ID do nó pai (None para raiz)
#         contrato: ID do contrato para filtrar
    
#     Returns:
#         Lista de dicionários com os nós
#     """
#     frappe.log_error(f"get_tree_nodes chamado - parent: {parent}, contrato: {contrato}", "Contract Item Tree")
    
#     if not contrato:
#         return []
    
#     # Determinar filtro do parent
#     filters = {
#         'contrato': contrato
#     }
    
#     # Se parent é None ou "All Contract Items" ou é o próprio contrato, buscar itens raiz
#     if not parent or parent == 'All Contract Items' or parent == contrato:
#         filters['parent_contract_item'] = ['is', 'not set']
#         frappe.log_error("Buscando itens RAIZ", "Contract Item Tree")
#     else:
#         filters['parent_contract_item'] = parent
#         frappe.log_error(f"Buscando filhos de: {parent}", "Contract Item Tree")
    
#     # Buscar itens
#     items = frappe.get_all(
#         'Contract Item',
#         filters=filters,
#         fields=['name', 'codigo', 'descricao', 'is_group', 'parent_contract_item'],
#         order_by='is_group desc, codigo asc'
#     )
    
#     frappe.log_error(f"Itens encontrados: {len(items)}", "Contract Item Tree")
    
#     # Formatar para a tree
#     nodes = []
#     for item in items:
#         # Montar título
#         title = ''
#         if item.get('codigo') and item.get('descricao'):
#             title = f"{item.codigo} - {item.descricao}"
#         elif item.get('codigo'):
#             title = item.codigo
#         elif item.get('descricao'):
#             title = item.descricao
#         else:
#             title = item.name
        
#         nodes.append({
#             'value': item.name,
#             'title': title,
#             'expandable': bool(item.is_group),
#             'is_group': bool(item.is_group)
#         })
    
#     return nodes

# @frappe.whitelist()
# def debug_contract_items(contrato):
#     """
#     Método de debug para verificar estrutura de itens
#     """
#     if not contrato:
#         return {"error": "Contrato não informado"}
    
#     # Buscar todos os itens do contrato
#     all_items = frappe.get_all(
#         'Contract Item',
#         filters={'contrato': contrato},
#         fields=['name', 'codigo', 'descricao', 'parent_contract_item', 'is_group'],
#         order_by='codigo asc'
#     )
    
#     # Separar raiz de filhos
#     root_items = [item for item in all_items if not item.get('parent_contract_item')]
#     child_items = [item for item in all_items if item.get('parent_contract_item')]
    
#     # Montar estrutura
#     structure = {
#         'total_items': len(all_items),
#         'root_items': len(root_items),
#         'child_items': len(child_items),
#         'root_list': root_items,
#         'child_list': child_items
#     }
    
#     # Log para debug
#     frappe.log_error(f"Debug Contract Items - Contrato: {contrato}", "Contract Item Debug")
#     frappe.log_error(f"Total: {len(all_items)}, Raiz: {len(root_items)}, Filhos: {len(child_items)}", "Contract Item Debug")
    
#     return structure