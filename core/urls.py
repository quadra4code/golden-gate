from django.urls import path
from core import views as CoreViews
urlpatterns = [
    path('request-land', CoreViews.create_land_request_view, name='request_land'),
    path('propose-land', CoreViews.propose_land_view, name='propose_land'),
    # path('login', UserViews.login_user, name='login'),
    # path('admin/login', UserViews.login_admin, name='login_admin'),
    # path('change-password', UserViews.change_password, name='change_password'),
    # path('logout', UserViews.test_sms, name='update_brands'),
    # path('delete-brands/<int:brand_id>', UserViews.delete_brand, name='delete_brands'),
]