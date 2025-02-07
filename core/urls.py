from django.urls import path
from core import views as CoreViews
urlpatterns = [
    path('propose-property', CoreViews.propose_property_view, name='propose_property'),
    # path('propose-unit', CoreViews.propose_unit_view, name='propose_unit'),
    path('request-property', CoreViews.request_property_view, name='request_property'),
    # path('request-unit', CoreViews.request_unit_view, name='request_unit'),
]