from django.urls import path
from admindash import views as AdminViews
urlpatterns = [
    path('staff_roles', AdminViews.staff_roles_view, name='staff_roles'),
    path('paginated-staff', AdminViews.paginated_staff_view, name='paginated_staff'),
    path('add-staff', AdminViews.add_staff_view, name='add_staff'),
    path('delete-staff/<int:staff_id>', AdminViews.delete_staff_view, name='delete_staff'),
    path('toggle-user-status/<int:user_id>', AdminViews.toggle_active_user_view, name='toggle_active_user'),
    path('paginated-clients', AdminViews.paginated_clients_view, name='paginated_clients'),
    path('paginated-unit-requests', AdminViews.paginated_unit_requests_view, name='paginated_unit_requests'),
    path('paginated-contact-us', AdminViews.paginated_contact_msgs_view, name='paginated_contact_us'),
    path('solve-contact-us/<int:msg_id>', AdminViews.solve_contact_msg_view, name='solve_contact_us'),
]