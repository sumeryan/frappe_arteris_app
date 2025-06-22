import frappe

@frappe.whitelist(methods=["GET"])
def check_holidays(year: int):
    """
    Check if there are holidays for a given year.
    :param year: Year to check for holidays.
    :return: List of holidays for the specified year.
    """
    if not year:
        return {"message": "Year is required."}

    new_year = frappe.db.get_value('Holiday', {'data': f'{year}-01-01'}, ['data'])

    if new_year:
        return {"update": False, "message": f"New Year already exists for the year {year}. (All holidays loaded)"}
    else:
        return {"update": True, "message": f"New Year does not exist for the year {year}. (Load holidays)"}

@frappe.whitelist(methods=["POST"])
def update_holidays():
    """
    Get current 
    """

    holidays_list = frappe.form_dict.holidays

    # Get all measurements for the contract
    for h in holidays_list:
        h_doctype = frappe.new_doc("Holiday")
        h_doctype.data = h['data']
        h_doctype.descricao = h['descricao']
        if h['uf']:
            h_doctype.uf = h['uf']
        h_doctype.save()

    return {"message": "Holidays updated successfully."}

