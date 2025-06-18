from django.urls import path
from core import views as CoreViews
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('propose-unit', CoreViews.propose_unit_view, name='propose_unit'),
    path('request-unit', CoreViews.request_unit_view, name='request_unit'),
    path('paginated-client-requests', CoreViews.paginated_client_requests_view, name='paginated_client_requests'),
    path('cancel-request/<int:request_id>', CoreViews.cancel_request_view, name='cancel_request'),
    path('get-form-data', CoreViews.proposal_form_data_view, name='get_form_data'),
    path('recent-units', CoreViews.recent_units_view, name='recent_units'),
    path('filter-paginated-units', CoreViews.filter_paginated_units_view, name='filter_paginated_units'),
    path('unit-details/<int:unit_id>', CoreViews.unit_details_view, name='unit_details'),
    path('paginated-client-units', CoreViews.paginated_client_units_view, name='paginated_client_units'),
    path('get-update-unit/<int:unit_id>', CoreViews.get_update_unit_view, name='get_update_unit'),
    path('update-unit', CoreViews.update_unit_view, name='update_unit'),
    path('delete-unit/<int:unit_id>', CoreViews.soft_delete_unit_view, name='soft_delete_unit'),
    path('hard-delete-unit/<int:unit_id>', CoreViews.hard_delete_unit_view, name='hard_delete_unit'),
    path('home-reviews', CoreViews.home_top_reviews_view, name='home_reviews'),
    path('home-articles', CoreViews.home_articles_view, name='home_articles'),
    path('home-consultation-types', CoreViews.home_consultation_types_view, name='home_consultations'),
    path('consultations/<int:consult_type_id>', CoreViews.consultations_by_type_view, name='consultation_details'),
    path('home-featured-units', CoreViews.home_featured_units_view, name='home_featured_units'),
    path('home-most-viewed-units', CoreViews.home_most_viewed_units_view, name='home_most_viewed_units'),
    path('draw-results', CoreViews.draw_results_view, name='draw_results'),
    path('add-review', CoreViews.add_review_view, name='add_review'),
    path('add-contact-us-msg', CoreViews.add_contact_us_msg_view, name='add_contact_us_msg'),
    path('add-favorite', CoreViews.add_favorite_view, name='add_favorite'),
    path('list-paginated-favorites', CoreViews.list_paginated_favorites_view, name='list_paginated_favorites'),
    path('delete-favorite/<int:favorite_id>', CoreViews.delete_favorite_view, name='delete_favorite'),
]

if settings.DEBUG:
  urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)