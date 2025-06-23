import frappe
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')
    except:
        return "R$ 0,00"

def formatar_percentual(valor):
    try:
        return f"{float(valor):.2f}%"
    except:
        return "0,00%"

def formatar_data(data_str):
    try:
        return frappe.utils.formatdate(data_str, "dd/mm/yyyy")
    except:
        return data_str
