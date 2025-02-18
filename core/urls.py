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
    path('home-consultations', CoreViews.home_consultations_view, name='home_consultations'),
    path('draw-results', CoreViews.draw_results_view, name='draw_results'),
    path('add-draw-result', CoreViews.add_draw_result_view, name='add_draw_result'),
    path('add-review', CoreViews.add_review_view, name='add_review'),
    path('createjson', CoreViews.createjson, name='add_draw_result'),
]