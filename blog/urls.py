from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('post/<slug:slug>/',views.post_detail,name='post_detail'),
    path('verify/<uidb64>/<token>/',views.verify_email,name='verify_email'),
    path('email-verification/',views.email_verification_notice,name='email_verification_notice'),
    path('forgot-password/',views.password_reset_request,name='password_reset_request'),
    path('reset-password/<uidb64>/<token>/',views.custom_password_reset_confirm,name='custom_password_reset_confirm'),
    path('create/',views.create_post,name='create_post'),
    path('post/<int:pk>/edit/',views.edit_post,name='edit_post'),
]