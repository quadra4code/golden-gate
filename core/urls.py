from django.urls import path
from core import views as CoreViews
urlpatterns = [
    path('propose-unit', CoreViews.propose_unit_view, name='propose_unit'),
    path('request-unit', CoreViews.request_unit_view, name='request_unit'),
    path('get-form-data', CoreViews.proposal_form_data_view, name='get-form-data'),
    path('all-units', CoreViews.all_units_view, name='all-units'),
    path('unit-details/<int:unit_id>', CoreViews.unit_details_view, name='unit_details'),
    path('filter-properties', CoreViews.filter_properties_view, name='filter-properties'),
    path('home-reviews', CoreViews.home_top_reviews_view, name='home_reviews'),
    path('home-articles', CoreViews.home_articles_view, name='home_articles'),
    path('home-consultation-types', CoreViews.home_consultation_types_view, name='home_consultations'),
    path('consultations/<int:consult_type_id>', CoreViews.consultations_by_type_view, name='consultation_details'),
    path('home-featured-units', CoreViews.home_featured_units_view, name='home_featured_units'),
    path('draw-results', CoreViews.draw_results_view, name='draw_results'),
    path('add-draw-result', CoreViews.add_draw_result_view, name='add_draw_result'),
    path('add-review', CoreViews.add_review_view, name='add_review'),
    path('add-contact-us-msg', CoreViews.add_contact_us_msg_view, name='add_contact_us_msg'),
    path('createjson', CoreViews.createjson, name='add_draw_result'),
]