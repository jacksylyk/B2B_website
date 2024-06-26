from django.urls import path, include
from users import views
from users.views import Register, registration_cancel, company_register_view, registration_finish, account_details, \
    company_details

# app_name = 'users'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register', Register.as_view(), name='register'),
    path('company_register', company_register_view, name='company_register'),
    path('registration_finish', registration_finish, name='registration_finish'),
    path('registration_cancel/', registration_cancel, name='registration_cancel'),
    path('account/', account_details, name='personal_account_detail'),
    path('company/update/', company_details, name='company_details'),
]
