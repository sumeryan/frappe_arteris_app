# import frappe
# from . import kartado_client
# from datetime import date, datetime

# @frappe.whitelist(methods=["POST"])
# def load_records(start_date: str, end_date: str):
    
#     split_start_date = start_date.split("-")
#     split_end_date = end_date.split("-")

#     date_start_date = datetime.combine(date(int(split_start_date[0]), int(split_start_date[1]), int(split_start_date[2])), datetime.min.time())
#     date_end_date = datetime.combine(date(int(split_end_date[0]), int(split_end_date[1]), int(split_end_date[2])), datetime.min.time())

#     k = kartado_client.KartadoClient(start_date=date_start_date, end_date=date_end_date)
#     k.get_measurement_records()

# import frappe
# from . import kartado_client
# from datetime import date, datetime
# import time

# # @frappe.whitelist(methods=["POST"])
# # def load_records(start_date: str, end_date: str):
# #     """
# #     Endpoint que enfileira o job de longa duração
# #     """
    
# #     # Enqueue na fila personalizada para jobs longos
# #     frappe.enqueue(
# #         load_records_background,
# #         queue="long",  # Fila personalizada
# #         timeout=14400,  # 4 horas
# #         is_async=True,
# #         now=False,
# #         job_name=f"Kartado Load {start_date} to {end_date}",
# #         enqueue_after_commit=True,  # Garante que executa após commit
# #         at_front=False,  # Não colocar na frente da fila
# #         track_job=True,  # Tracking para monitoramento
# #         start_date=start_date,
# #         end_date=end_date        
# #     )
    
# #     # # Criar um registro de controle para acompanhar o job
# #     # job_tracker = frappe.get_doc({
# #     #     "doctype": "Background Job Tracker",  # Você pode criar este DocType
# #     #     "job_id": job.id,
# #     #     "job_name": f"Kartado Load {start_date} to {end_date}",
# #     #     "status": "Queued",
# #     #     "start_date": start_date,
# #     #     "end_date": end_date,
# #     #     "user": frappe.session.user,
# #     #     "estimated_duration": "2-4 hours"
# #     # })
# #     # job_tracker.insert()
    
# #     return {
# #         "message": "Job de longa duração enfileirado com sucesso",
# #         "status": "queued",
# #         # "job_id": job.id,
# #         # "tracker_id": job_tracker.name,
# #         "estimated_time": "2-4 horas"
# #     }

# # def load_records_background(start_date: str, end_date: str):
# #     """
# #     Função otimizada para processamento de longa duração
# #     """
# #     job_start_time = time.time()
    
# #     try:
# #         # # Notificar início
# #         # frappe.publish_realtime(
# #         #     'kartado_job_update', 
# #         #     {
# #         #         'status': 'started',
# #         #         'message': 'Iniciando processamento de longa duração...',
# #         #         'start_time': frappe.utils.now()
# #         #     },
# #         #     user=frappe.session.user
# #         # )
        
# #         # Processar datas
# #         split_start_date = start_date.split("-")
# #         split_end_date = end_date.split("-")

# #         date_start_date = datetime.combine(
# #             date(int(split_start_date[0]), int(split_start_date[1]), int(split_start_date[2])), 
# #             datetime.min.time()
# #         )
# #         date_end_date = datetime.combine(
# #             date(int(split_end_date[0]), int(split_end_date[1]), int(split_end_date[2])), 
# #             datetime.min.time()
# #         )

# #         # # Checkpoint 1: Inicialização
# #         # frappe.publish_realtime(
# #         #     'kartado_job_update', 
# #         #     {
# #         #         'status': 'processing',
# #         #         'progress': 10,
# #         #         'message': 'Conectando ao Kartado...',
# #         #         'elapsed_time': f"{int(time.time() - job_start_time)}s"
# #         #     },
# #         #     user=frappe.session.user
# #         # )

# #         # Inicializar cliente com configurações otimizadas
# #         k = kartado_client.KartadoClient(
# #             start_date=date_start_date, 
# #             end_date=date_end_date
# #         )
        
# #         # # Checkpoint 2: Início do processamento principal
# #         # frappe.publish_realtime(
# #         #     'kartado_job_update', 
# #         #     {
# #         #         'status': 'processing',
# #         #         'progress': 20,
# #         #         'message': 'Iniciando carregamento de registros...',
# #         #         'elapsed_time': f"{int(time.time() - job_start_time)}s"
# #         #     },
# #         #     user=frappe.session.user
# #         # )

# #         k.get_measurement_records()
        
# #         # # Checkpoint final
# #         # total_time = int(time.time() - job_start_time)
# #         # frappe.publish_realtime(
# #         #     'kartado_job_update', 
# #         #     {
# #         #         'status': 'completed',
# #         #         'progress': 100,
# #         #         'message': f'✅ Processamento concluído! {result.get("records_count", 0)} registros processados',
# #         #         'total_time': f"{total_time}s ({total_time//60}min)",
# #         #         'end_time': frappe.utils.now()
# #         #     },
# #         #     user=frappe.session.user
# #         # )
        
# #         # Log detalhado
# #         frappe.logger().info(f"Kartado job completed successfully in {total_time}s. Records: {result.get('records_count', 0)}")
        
# #         # return result
        
# #     except Exception as e:
# #         total_time = int(time.time() - job_start_time)
# #         error_msg = f"Erro após {total_time}s: {str(e)}"
        
# #         frappe.publish_realtime(
# #             'kartado_job_update', 
# #             {
# #                 'status': 'failed',
# #                 'progress': -1,
# #                 'message': f'❌ {error_msg}',
# #                 'total_time': f"{total_time}s",
# #                 'error': str(e)
# #             },
# #             user=frappe.session.user
# #         )
        
# #         frappe.logger().error(f"Kartado job failed after {total_time}s: {str(e)}")
# #         raise