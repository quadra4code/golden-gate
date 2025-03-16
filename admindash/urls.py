from django.urls import path
from admindash import views as AdminViews
urlpatterns = [
    path('main-statistics', AdminViews.main_statistics_view, name='main_statistics'),
    path('active-visitors', AdminViews.active_visitors_view, name='active_visitors'),
    path('staff-login', AdminViews.staff_login_view, name='staff_login'),
    path('staff-roles', AdminViews.staff_roles_view, name='staff_roles'),
    path('paginated-staff', AdminViews.paginated_staff_view, name='paginated_staff'),
    path('add-staff', AdminViews.add_staff_view, name='add_staff'),
    path('delete-staff/<int:staff_id>', AdminViews.delete_staff_view, name='delete_staff'),
    path('toggle-user-status/<int:user_id>', AdminViews.toggle_active_user_view, name='toggle_active_user'),
    path('change-staff-permissions', AdminViews.change_staff_permissions_view, name='change_staff_permissions'),
    path('get-sales-staff', AdminViews.get_sales_staff_view, name='get_sales_staff'),
    path('paginated-clients', AdminViews.paginated_clients_view, name='paginated_clients'),
    path('reset-password/<int:user_id>', AdminViews.reset_password_view, name='reset_password'),
    path('paginated-units', AdminViews.paginated_units_view, name='paginated_units'),
    path('unit-requests-user/<int:unit_id>', AdminViews.unit_requests_user_view, name='unit_requests_user'),
    path('update-unit-status/<int:unit_id>/<int:status_id>', AdminViews.update_unit_status_view, name='update_unit_status'),
    path('toggle-unit-hide/<int:unit_id>', AdminViews.toggle_unit_deleted_view, name='toggle_unit_hide'),
    path('paginated-requests', AdminViews.paginated_requests_view, name='paginated_requests'),
    path('change-request-status', AdminViews.change_request_status_view, name='change_request_status'),
    path('assign-sales-request', AdminViews.assign_sales_request_view, name='assign_sales_request'),
    path('paginated-contact-us', AdminViews.paginated_contact_msgs_view, name='paginated_contact_us'),
    path('solve-contact-us/<int:msg_id>', AdminViews.solve_contact_msg_view, name='solve_contact_us'),
    path('delete-contact-us/<int:msg_id>', AdminViews.delete_contact_msg_view, name='delete_contact_us'),
    path('create-article', AdminViews.create_article_view, name='create_article'),
    path('all-articles', AdminViews.read_articles_view, name='all_articles'),
    path('update-article/<int:article_id>', AdminViews.update_article_view, name='update_article'),
    path('delete-article/<int:article_id>', AdminViews.delete_article_view, name='delete_article'),
    path('toggle-hidden-article/<int:article_id>', AdminViews.toggle_hidden_article_view, name='toggle_hidden_article'),
    path('create-consult-type', AdminViews.create_consult_type_view, name='create_consult_type'),
    path('all-consult-types', AdminViews.read_consult_types_view, name='all_consult_types'),
    path('update-consult-type/<int:consult_type_id>', AdminViews.update_consult_type_view, name='update_consult_type'),
    path('delete-consult-type/<int:consult_type_id>', AdminViews.delete_consult_type_view, name='delete_consult_type'),
    path('toggle-hidden-consult-type/<int:consult_type_id>', AdminViews.toggle_hidden_consult_type_view, name='toggle_hidden_consult_type'),
    path('create-consultation', AdminViews.create_consultation_view, name='create_consultation'),
    path('all-consultations/<int:consult_type_id>', AdminViews.read_consultations_view, name='all_consultation'),
    path('update-consultation/<int:consultation_id>', AdminViews.update_consultation_view, name='update_consultation'),
    path('delete-consultation/<int:consultation_id>', AdminViews.delete_consultation_view, name='delete_consultation'),
    path('toggle-hidden-consultation/<int:consultation_id>', AdminViews.toggle_hidden_consultation_view, name='toggle_hidden_consultation'),
]