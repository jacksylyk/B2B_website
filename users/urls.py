from django.urls import path, include
from users import views
from users.views import Register, CompanyRegister, registration_cancel

# app_name = 'users'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register', Register.as_view(), name='register'),
    path('company_register', CompanyRegister.as_view(), name='company_register'),
    path('registration_cancel/', registration_cancel, name='registration_cancel'),
]
