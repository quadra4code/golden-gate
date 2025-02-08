from django.urls import path
from core import views as CoreViews
urlpatterns = [
    path('propose-property', CoreViews.propose_property_view, name='propose_property'),
    path('request-property', CoreViews.request_property_view, name='request_property'),
    path('get-form-data', CoreViews.proposal_form_data_view, name='get-form-data'),
    path('all-properties', CoreViews.all_properties_view, name='all-properties'),
    path('filter-properties', CoreViews.filter_properties_view, name='filter-properties'),

]