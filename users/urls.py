from django.urls import path
from users import views as UserViews
urlpatterns = [
    path('register', UserViews.register_user_view, name='register_user'),
    path('login', UserViews.login_user_view, name='login_user'),
    # path('admin/login', UserViews.login_admin, name='login_admin'),
    path('change-password', UserViews.change_password_view, name='change_password'),
    # path('logout', UserViews.test_sms, name='update_brands'),
    # path('delete-brands/<int:brand_id>', UserViews.delete_brand, name='delete_brands'),
]