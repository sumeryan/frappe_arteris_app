# import frappe
# from . import osiris_client
# from datetime import date, datetime

# @frappe.whitelist(methods=["POST"])
# def get_measurement_records(start_date: str, end_date: str):
    
#     split_start_date = start_date.split("-")
#     split_end_date = end_date.split("-")

#     date_start_date = datetime.combine(date(int(split_start_date[0]), int(split_start_date[1]), int(split_start_date[2])), datetime.min.time())
#     date_end_date = datetime.combine(date(int(split_end_date[0]), int(split_end_date[1]), int(split_end_date[2])), datetime.min.time())

#     o = osiris_client.OsirisClient(start_date=date_start_date, end_date=date_end_date)
#     o.get_measurement_records()