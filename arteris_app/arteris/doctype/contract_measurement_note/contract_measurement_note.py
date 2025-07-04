# Copyright (c) 2025, Renoir and contributors
# For license information, please see license.txt

import frappe
import json  # ADICIONADO: import json que estava faltando
from frappe.model.document import Document
from arteris_app.api.measurement import create_measurement


class ContractMeasurementNote(Document):


    def before_cancel(self):

        # Get measurement record
        measurement_record = frappe.db.get_value(
            "Contract Measurement Record", 
            {"apontamentodireto": self.name},
            ["name"]
        )
        # Delete measurement record if exists
        if measurement_record:
            frappe.delete_doc("Contract Measurement Record", measurement_record)



    def before_submit(self):

        # Get note
        get_note = frappe.get_doc('Contract Measurement Note', self.name)

        # Get datetime
        current_date = frappe.utils.now_datetime()

        # Get measurement
        measurement = create_measurement(
            month=current_date.month, 
            year=current_date.year, 
            ignore_current_measurement=False,
            contract=get_note.contrato
        )

        get_note.boletim = measurement['measurements'][0]['name']
        get_note.datainicial = measurement['measurements'][0]['start']
        get_note.datafinal = measurement['measurements'][0]['end']
        get_note.datasubmissao = current_date
        get_note.save()

        # Create measurement record
        measurement_record = frappe.new_doc("Contract Measurement Record")
        measurement_record.tipo = f"Apontamento direto - {get_note.contrato}"
        measurement_record.datacriacao = current_date
        measurement_record.dataexecucao = current_date
        measurement_record.dataaprovacao = current_date
        measurement_record.contrato = get_note.contrato
        measurement_record.boletimmedicao = measurement['measurements'][0]['name']
        measurement_record.kminicial = 0
        measurement_record.kmfinal = 0
        measurement_record.medicaovigente =measurement['measurements'][0]['current']
        measurement_record.aprovador = frappe.utils.get_fullname()
        measurement_record.eh_feriado = False
        measurement_record.apontamentodireto = get_note.name
        measurement_record.origem_integracao = "Apontamento direto"

        # Create measurement record for each work role
        for wr in get_note.tabfuncoes:
            measurement_work_role_record = measurement_record.append("tabworkrole")
            measurement_work_role_record.item = wr.item
            measurement_work_role_record.funcao = wr.funcao
            measurement_work_role_record.quantidademedida = wr.quantidade
            measurement_work_role_record.valortotal = wr.valortotal
            measurement_work_role_record.valorcalculado = wr.valortotal

        # Create measurement record for each asset
        for asset in get_note.tabativos:
            measurement_asset_record = measurement_record.append("tabasset")
            measurement_asset_record.item = asset.item
            measurement_asset_record.maquina_equipamento_ou_ferramenta = asset.ativo
            measurement_asset_record.quantidademedida = asset.quantidade
            measurement_asset_record.valortotal = asset.valortotal
            measurement_asset_record.valorcalculado = asset.valortotal

        # Create measurement record for each sap order
        for order in get_note.tabsap:

            # Get SAP Order
            pedido_sap = frappe.db.get_value(
                "SAP Order Period", 
                {"name": order.pedidolinha},
                ["parent"]
            )

            measurement_order_record = measurement_record.append("taborder")
            measurement_order_record.pedidosap = pedido_sap
            measurement_order_record.linhapedido = order.pedidolinha
            measurement_order_record.valormedido = order.valormedido

        # Create measurement record for each item
        for item in get_note.tabitem:
            measurement_reseource_record = measurement_record.append("tabrecurso")
            measurement_reseource_record.item = item.item
            measurement_reseource_record.quantidademedida = item.quantidademedida
            measurement_reseource_record.valortotal = item.valormedido
            measurement_reseource_record.valorcalculado = item.valormedido

        measurement_record.save()

@frappe.whitelist()
def get_contract_data(contrato=None):
    """
    Retorna múltiplos detalhes do contrato
    """
    
    if not contrato:
        return {}
    
    # Query base - busca por função
    base_query = """
        SELECT DISTINCT
            subsidiary.nome as subsidiaria,
            contracted.nome as contratada
        FROM 
            `tabContract` contract
            INNER JOIN `tabSubsidiary` subsidiary ON subsidiary.name=contract.subsidiaria
            INNER JOIN `tabContracted Company` contracted ON contracted.name=contract.contratada
        WHERE 
            contract.name = %s
        LIMIT 1 
    """
    
    params = [contrato]
    
    details = frappe.db.sql(base_query, tuple(params), as_dict=True)
    
    if details and len(details) > 0:
        return {
            'subsidiaria': details[0].get('subsidiaria'),
            'contratada': details[0].get('contratada'),
        }
    
    return {}
    

@frappe.whitelist()
def get_sap_order_line(doctype, txt, searchfield, start, page_len, filters):
    """
    Busca linhas do pedido SAP específico
    """
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    contrato = filters.get('contrato', '')
    
    # Se não tiver pedido_sap, retorna vazio
    if not contrato:
        return []
    
    return frappe.db.sql("""
        SELECT DISTINCT
            child.name AS value,
            CONCAT(child.name,' - ',child.centrodecusto) AS label
        FROM 
            `tabSAP Order Period` child
            INNER JOIN `tabContract Item Order` item_order ON item_order.pedidosap = child.parent
            INNER JOIN `tabContract Item` item ON item.name = item_order.parent
        WHERE 
            item.contrato = %(contrato)s
            AND (child.name LIKE %(txt)s OR child.centrodecusto LIKE %(txt)s)
        ORDER BY 
            child.idx, child.name
        LIMIT %(start)s, %(page_len)s""", {
        'contrato': contrato,
        'txt': '%%%s%%' % txt,
        'start': int(start),
        'page_len': int(page_len)
    })

@frappe.whitelist()
def get_sap_order_line_cc(pedido_linha):
    """
    Retorna o valor de um campo selecionado
    """
    if not pedido_linha:
        return None
    
    centro_custo = frappe.db.sql("""
        SELECT DISTINCT
            child.centrodecusto
        FROM 
            `tabSAP Order Period` child
        WHERE 
            child.name = %s
        LIMIT 1
    """, (pedido_linha,), as_dict=True)
    
    if centro_custo and len(centro_custo) > 0:
        return {
            'codigocc': centro_custo[0].get('centrodecusto')
        }
    
    return None

@frappe.whitelist()
def get_work_role(doctype, txt, searchfield, start, page_len, filters):
    """
    Busca funcoes especificas do contrato
    """
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    contrato = filters.get('contrato', '')
    
    # Se não tiver contrato, retorna vazio
    if not contrato:
        return []
    
    return frappe.db.sql("""
        SELECT DISTINCT
            wk.name AS value,
            wk.funcao AS label      
        FROM 
            `tabContract Item Work Role` child
            INNER JOIN `tabWork Role` wk ON wk.name = child.funcao
            INNER JOIN `tabContract Item` item ON item.name = child.parent
        WHERE 
            item.contrato = %(contrato)s
            AND (wk.name LIKE %(txt)s)
        ORDER BY 
            wk.funcao
        LIMIT %(start)s, %(page_len)s""", {
        'contrato': contrato,
        'txt': '%%%s%%' % txt,
        'start': int(start),
        'page_len': int(page_len)
    })

@frappe.whitelist()
def get_work_role_item(doctype, txt, searchfield, start, page_len, filters):
    """
    Busca itens específicos para uma função de trabalho em um contrato
    """
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    contrato = filters.get('contrato', '')
    funcao = filters.get('funcao', '')  # CORRIGIDO: mudou de 'work_role' para 'funcao'
    
    if not contrato or not funcao:
        return []
    
    result = frappe.db.sql("""
        SELECT DISTINCT
            item.name AS value,
            item.descricao AS label      
        FROM 
            `tabContract Item Work Role` child
            INNER JOIN `tabContract Item` item ON item.name = child.parent
            INNER JOIN `tabWork Role` wk ON wk.name = child.funcao
        WHERE 
            item.contrato = %(contrato)s
            AND child.funcao = %(funcao)s
            AND (item.name LIKE %(txt)s OR item.codigo LIKE %(txt)s OR item.descricao LIKE %(txt)s)
        ORDER BY 
            item.codigo, item.descricao
        LIMIT %(start)s, %(page_len)s""", {
        'contrato': contrato,
        'funcao': funcao,  # CORRIGIDO: usar 'funcao'
        'txt': '%%%s%%' % txt,
        'start': int(start),
        'page_len': int(page_len)
    })
    
    return result

@frappe.whitelist()
def get_work_role_data(funcao=None, item=None, contrato=None):
    """
    Retorna múltiplos detalhes da funcao selecionada
    Aceita tanto os novos parâmetros (funcao, item, contrato) quanto o antigo (funcao_linha)
    """
    
    if not funcao or not item or not contrato:
        return {}
    
    # Query base - busca por função
    base_query = """
        SELECT DISTINCT
            child.valortotalmensal,
            child.valorporhora
        FROM 
            `tabContract Item Work Role` child 
            INNER JOIN `tabContract Item` item ON item.name = child.parent
        WHERE 
            child.funcao = %s
            AND item.name = %s
            AND item.contrato = %s
        LIMIT 1 
    """
    
    params = [funcao, item, contrato]
    
    details = frappe.db.sql(base_query, tuple(params), as_dict=True)
    
    if details and len(details) > 0:
        return {
            'valormensal': details[0].get('valortotalmensal'),
            'valorporhora': details[0].get('valorporhora'),
        }
    
    return {}
    
@frappe.whitelist()
def get_asset(doctype, txt, searchfield, start, page_len, filters):
    """
    Busca ativos especificas do contrato
    """
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    contrato = filters.get('contrato', '')
    
    # Se não tiver contrato, retorna vazio
    if not contrato:
        return []
    
    return frappe.db.sql("""
        SELECT DISTINCT
            asset.name AS value,
            asset.nomeativo AS label      
        FROM 
            `tabContract Item Asset` child
            INNER JOIN `tabAsset` asset ON asset.name = child.asset
            INNER JOIN `tabContract Item` item ON item.name = child.parent
        WHERE 
            item.contrato = %(contrato)s
            AND (asset.nomeativo LIKE %(txt)s)
        ORDER BY 
            asset.nomeativo
        LIMIT %(start)s, %(page_len)s""", {
        'contrato': contrato,
        'txt': '%%%s%%' % txt,
        'start': int(start),
        'page_len': int(page_len)
    })

@frappe.whitelist()
def get_asset_item(doctype, txt, searchfield, start, page_len, filters):
    """
    Busca itens específicos para um ativo de um contrato
    """
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    contrato = filters.get('contrato', '')
    ativo = filters.get('ativo', '')  
    
    if not contrato or not ativo:
        return []
    
    result = frappe.db.sql("""
        SELECT DISTINCT
            item.name AS value,
            item.descricao AS label      
        FROM 
            `tabContract Item Asset` child
            INNER JOIN `tabContract Item` item ON item.name = child.parent
        WHERE 
            item.contrato = %(contrato)s
            AND child.asset = %(ativo)s
            AND (item.name LIKE %(txt)s OR item.codigo LIKE %(txt)s OR item.descricao LIKE %(txt)s)
        ORDER BY 
            item.codigo, item.descricao
        LIMIT %(start)s, %(page_len)s""", {
        'contrato': contrato,
        'ativo': ativo,  
        'txt': '%%%s%%' % txt,
        'start': int(start),
        'page_len': int(page_len)
    })
    
    return result

@frappe.whitelist()
def get_asset_data(ativo=None, item=None, contrato=None):
    """
    Retorna múltiplos detalhes do ativo selecionado
    """
    
    if not ativo or not item or not contrato:
        return {}
    
    # Query base - busca por função
    base_query = """
        SELECT DISTINCT
            child.valorunitario,
            child.valormensal
        FROM 
            `tabContract Item Asset` child
            INNER JOIN `tabContract Item` item ON item.name = child.parent
        WHERE 
            child.asset = %s
            AND item.name = %s
            AND item.contrato = %s
        LIMIT 1 
    """
    
    params = [ativo, item, contrato]
    
    details = frappe.db.sql(base_query, tuple(params), as_dict=True)
    
    if details and len(details) > 0:
        return {
            'valorunitario': details[0].get('valorunitario'),
            'valormensal': details[0].get('valormensal'),
        }
    
    return {}
    
