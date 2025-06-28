from django.urls import path
from admindash import views as AdminViews
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('main-statistics', AdminViews.main_statistics_view, name='main_statistics'),
    path('active-visitors-count', AdminViews.active_visitors_count_view, name='active_visitors_count'),
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
    path('paginated-featured-units', AdminViews.paginated_featured_units_view, name='paginated_featured_units'),
    path('paginated-new-units', AdminViews.paginated_units_addition_requests_view, name='paginated_units_addition_requests'),
    path('paginated-rejected-units', AdminViews.paginated_rejected_units_view, name='paginated_rejected_units'),
    path('paginated-trashed-units', AdminViews.paginated_soft_deleted_units_view, name='paginated_soft_deleted_units'),
    path('unit-requests-user/<int:unit_id>', AdminViews.unit_requests_user_view, name='unit_requests_user'),
    path('update-unit-status/<int:unit_id>/<int:status_id>', AdminViews.update_unit_status_view, name='update_unit_status'),
    path('toggle-unit-hide/<int:unit_id>', AdminViews.toggle_unit_deleted_view, name='toggle_unit_hide'),
    path('reset-unit-approval/<int:unit_id>', AdminViews.reset_unit_approval_view, name='reset_unit_approval'),
    path('toggle-unit-featured/<int:unit_id>', AdminViews.toggle_unit_featured_view, name='toggle_unit_featured'),
    path('approve-unit/<int:unit_id>', AdminViews.approve_unit_addition_view, name='approve_unit_addition'),
    path('disapprove-unit', AdminViews.disapprove_unit_addition_view, name='disapprove_unit_addition'),
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
    path('paginated-reviews', AdminViews.read_reviews_view, name='paginated_reviews'),
    path('toggle-hidden-review/<int:review_id>', AdminViews.toggle_hidden_review_view, name='toggle_hidden_review'),
    path('delete-review/<int:review_id>', AdminViews.delete_review_view, name='delete_review'),
    # region Unit Type
    path('create-unit-type', AdminViews.create_unit_type_view, name='create_unit_type'),
    path('all-unit-types', AdminViews.read_unit_types_view, name='all_unit_types'),
    path('update-unit-type/<int:unit_type_id>', AdminViews.update_unit_type_view, name='update_unit_type'),
    path('delete-unit-type/<int:unit_type_id>', AdminViews.delete_unit_type_view, name='delete_unit_type'),
    path('toggle-hidden-unit-type/<int:unit_type_id>', AdminViews.toggle_hidden_unit_type_view, name='toggle_hidden_unit_type'),
    # endregion
    # region Proposal
    path('create-proposal', AdminViews.create_proposal_view, name='create_proposal'),
    path('all-proposals', AdminViews.read_proposals_view, name='all_proposals'),
    path('update-proposal/<int:proposal_id>', AdminViews.update_proposal_view, name='update_proposal'),
    path('delete-proposal/<int:proposal_id>', AdminViews.delete_proposal_view, name='delete_proposal'),
    path('toggle-hidden-proposal/<int:proposal_id>', AdminViews.toggle_hidden_proposal_view, name='toggle_hidden_proposal'),
    # endregion
    # region Project
    path('create-project', AdminViews.create_project_view, name='create_project'),
    path('all-projects', AdminViews.read_projects_view, name='all_projects'),
    path('update-project/<int:project_id>', AdminViews.update_project_view, name='update_project'),
    path('delete-project/<int:project_id>', AdminViews.delete_project_view, name='delete_project'),
    path('toggle-hidden-project/<int:project_id>', AdminViews.toggle_hidden_project_view, name='toggle_hidden_project'),
    # endregion
    # region City
    path('create-city', AdminViews.create_city_view, name='create_city'),
    path('all-cities', AdminViews.read_cities_view, name='all_cities'),
    path('update-city/<int:city_id>', AdminViews.update_city_view, name='update_city'),
    path('delete-city/<int:city_id>', AdminViews.delete_city_view, name='delete_city'),
    path('toggle-hidden-city/<int:city_id>', AdminViews.toggle_hidden_city_view, name='toggle_hidden_city'),
    # endregion
    # region Region
    path('create-region', AdminViews.create_region_view, name='create_region'),
    path('all-regions', AdminViews.read_regions_view, name='all_regions'),
    path('update-region/<int:region_id>', AdminViews.update_region_view, name='update_region'),
    path('delete-region/<int:region_id>', AdminViews.delete_region_view, name='delete_region'),
    path('toggle-hidden-region/<int:region_id>', AdminViews.toggle_hidden_region_view, name='toggle_hidden_region'),
    # endregion
    # region Status
    path('create-status', AdminViews.create_status_view, name='create_status'),
    path('all-status', AdminViews.read_status_view, name='all_status'),
    path('update-status/<int:status_id>', AdminViews.update_status_view, name='update_status'),
    path('delete-status/<int:status_id>', AdminViews.delete_status_view, name='delete_status'),
    path('toggle-hidden-status/<int:status_id>', AdminViews.toggle_hidden_status_view, name='toggle_hidden_status'),
    # endregion

]

if settings.DEBUG:
  urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)