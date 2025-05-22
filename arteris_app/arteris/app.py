import frappe

@frappe.whitelist(allow_guest=True)
def get_ping():
    return "pong"


# @frappe.whitelist(allow_guest=True)
# def get_kartado_maps():
#     """
#     Function to get the kartado maps.
#     """

#     asset_data = fappre.db.sql("""
#         SELECT
#             a.`name` AS `assett`,
#             a.`ativo` AS `ativo`,
#             k.`descricao` AS `ativo_kartado`
#         FROM
#             `tabAsset` as a
#             INNER JOIN `tabAsset Config Kartado`.`parent` as k ON k.`name` = a.`parent`  
#         """)

#     work_map = fappre.db.sql("""
#         SELECT
#             w.`name` AS `assett`,
#             w.`funcao` AS `funcao`,
#             k.`descricaokartado` AS `funcao_kartado`
#         FROM
#             `tabWork Role` as w
#             INNER JOIN `tabWork Role Config Kartado`.`parent` as k ON k.`name` = a.`parent`  
#         """)

#     data = {
#         "asset_data": asset_data,
#         "work_map": work_map
#     }
   
#     # Return the kartado maps
#     return data

