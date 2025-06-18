from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from users import views as UserViews

urlpatterns = [
    path('register', UserViews.register_user_view, name='register_user'),
    path('login', UserViews.login_user_view, name='login_user'),
    path('change-password', UserViews.change_password_view, name='change_password'),
    path('account-view', UserViews.account_view, name='account_view'),
    path('update-account', UserViews.update_account_view, name='update_account'),
    path('leaderboard', UserViews.leaderboard_view, name='leaderboard'),
]

if settings.DEBUG:
  urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)