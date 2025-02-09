from django.urls import path
from core import views as CoreViews
urlpatterns = [
    path('propose-property', CoreViews.propose_property_view, name='propose_property'),
    path('request-property', CoreViews.request_property_view, name='request_property'),
    path('get-form-data', CoreViews.proposal_form_data_view, name='get-form-data'),
    path('all-properties', CoreViews.all_properties_view, name='all-properties'),
    path('filter-properties', CoreViews.filter_properties_view, name='filter-properties'),
    path('home-reviews', CoreViews.home_top_reviews_view, name='home_reviews'),
    path('home-articles', CoreViews.home_articles_view, name='home_articles'),
    path('home-consultations', CoreViews.home_consultations_view, name='home_consultations'),
    path('draw-results', CoreViews.draw_results_view, name='draw_results'),
    path('add-draw-result', CoreViews.add_draw_result_view, name='add_draw_result'),
]