from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "myapp"

urlpatterns = [
    path("", views.home, name="home"),
    path("tours/", views.tour_list, name="tour_list"),
    path("tours/<int:tour_id>/", views.tour_detail, name="tour_detail"),
    path("tours/<int:tour_id>/book/", views.create_booking, name="create_booking"),
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/<int:booking_id>/receipt/", views.booking_receipt, name="booking_receipt"),
    path("profile/", views.profile, name="profile"),
    path("notifications/", views.message_notifications, name="message_notifications"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("contact/", views.contact, name="contact"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.CustomLoginView.as_view(
        template_name="registration/login.html"
    ), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/password-reset/", auth_views.PasswordResetView.as_view(
        template_name="registration/password_reset_form.html"
    ), name="password_reset"),
    path("accounts/password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="registration/password_reset_done.html"
    ), name="password_reset_done"),
    path("accounts/reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="registration/password_reset_confirm.html"
    ), name="password_reset_confirm"),
    path("accounts/reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="registration/password_reset_complete.html"
    ), name="password_reset_complete"),
]
